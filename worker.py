"""worker.py - runs ONE built-in candidate in a separate process.

Protocol: reads one JSON list per line from stdin, writes one JSON result per line.
Started by sandbox.py. Never imported by the app.
"""

import json
import sys

proto = sys.stdout        # keep the real stdout for results only
sys.stdout = sys.stderr   # anything the candidate prints goes to stderr, not the protocol

try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))             # max 60 CPU-seconds
    if sys.platform.startswith("linux"):                          # memory cap works on Linux
        resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))  # 1 GB
except Exception:
    pass

from problems import PROBLEMS  # noqa: E402


def main():
    key, name = sys.argv[1], sys.argv[2]
    func = PROBLEMS[key]["candidates"][name]
    proto.write(json.dumps({"ready": True}) + "\n")
    proto.flush()
    for line in sys.stdin:
        arr = json.loads(line)
        try:
            out = {"status": "ok", "value": func(arr)}
            json.dumps(out)  # make sure the output is serialisable
        except Exception as exc:
            out = {"status": "error", "value": f"{type(exc).__name__}: {exc}"}
        proto.write(json.dumps(out) + "\n")
        proto.flush()


main()
