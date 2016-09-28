import os
from collections import deque

import execute
from util import PersistentVariable

if __name__ == "__main__":
    PersistentVariable.clear()
    execute.Executor.create_history()
    num_paths = PersistentVariable("total")
    unique_branches = PersistentVariable("branches")
    errors = PersistentVariable("errors")
    completed = PersistentVariable("complete")
    paths = PersistentVariable("paths")
    paths.value = deque()  # queue of frontier nodes.
    num_paths.value = 0
    unique_branches.value = set()
    errors.value = 0
    completed.value = False
