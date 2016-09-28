from __future__ import print_function

import os

import execute
from util import PersistentVariable

if __name__ == "__main__":
    num_paths = PersistentVariable("total")
    unique_branches = PersistentVariable("branches")
    errors = PersistentVariable("errors")
    completed = PersistentVariable("complete")
    print()
    print("Errors:", errors.value)
    print("Unique Branches:", unique_branches.value)
    print("Num Branches:", len(unique_branches.value))
    print("Paths:", num_paths.value)
    print("Completed:", completed.value)

    try:
        os.remove(execute.PICKLE)
    except OSError:
        pass

