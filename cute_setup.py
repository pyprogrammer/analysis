import os

import execute
from util import PersistentVariable

if __name__ == "__main__":
    execute.Executor.create_history()
    num_paths = PersistentVariable("total")
    unique_branches = PersistentVariable("branches")
    errors = PersistentVariable("errors")
    completed = PersistentVariable("complete")
    num_paths.value = 0
    unique_branches.value = set()
    errors.value = 0
    completed.value = False
    try:
        os.remove(execute.PICKLE)
    except OSError:
        pass
