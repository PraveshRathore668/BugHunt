"""sandbox.py - runs a built-in candidate in a worker process with a per-call timeout.

Not a full security sandbox. It protects the app from hangs and crashes in
built-in candidates and is the place a stronger runner can be plugged in later.
"""

import json
import os
import select
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.join(HERE, "worker.py")


class CandidateRunner:
    def __init__(self, problem_key, candidate_name, timeout=2.0):
        self.problem_key = problem_key
        self.candidate_name = candidate_name
        self.timeout = timeout
        self.proc = None

    def _start(self):
        self.proc = subprocess.Popen(
            [sys.executable, WORKER, self.problem_key, self.candidate_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            cwd=HERE,
            env={"PATH": os.environ.get("PATH", "")},  # no secrets from our environment
        )
        ready, _, _ = select.select([self.proc.stdout], [], [], 10)
        line = self.proc.stdout.readline() if ready else ""
        if not line or not json.loads(line).get("ready"):
            self._kill()
            raise RuntimeError("worker process failed to start")

    def _kill(self):
        if self.proc is not None:
            try:
                self.proc.kill()
                self.proc.wait(timeout=5)
            except Exception:
                pass
            self.proc = None

    def call(self, arr):
        """Returns ("ok", value), ("error", message) or ("timeout", message)."""
        if self.proc is None or self.proc.poll() is not None:
            self._start()
        try:
            self.proc.stdin.write(json.dumps(arr) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError):
            self._kill()
            return "error", "WorkerCrashed: candidate process died"
        ready, _, _ = select.select([self.proc.stdout], [], [], self.timeout)
        if not ready:
            self._kill()
            return "timeout", f"no result within {self.timeout} s"
        line = self.proc.stdout.readline()
        if not line:
            self._kill()
            return "error", "WorkerCrashed: candidate process died"
        msg = json.loads(line)
        return msg["status"], msg["value"]

    def close(self):
        self._kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
