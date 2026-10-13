from problems import *

print(max_element_ref([-5, -2, -9]), max_element_bug_zero_init([-5, -2, -9]))
print(max_element_ref([1, 2, 9]), max_element_bug_skip_last([1, 2, 9]))
print(second_largest_ref([5, 5, 3]), second_largest_bug_duplicates([5, 5, 3]))
print(second_largest_ref([7, 7]), second_largest_bug_all_equal([7, 7]))
print(max_subarray_ref([-3, -1, -2]), max_subarray_bug_zero_init([-3, -1, -2]))
print(max_subarray_ref([-1, 5]), max_subarray_bug_skip_last([-1, 5]))
