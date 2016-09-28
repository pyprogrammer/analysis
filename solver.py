import subprocess
from collections import deque

from util import PersistentVariable

import path

PATH_TO_YICES = "/Users/nzhang-dev/Documents/Fall16/CS294-15/cute/yices-1.0.40/bin/yices"
MAXINT = 2**31 - 1
MININT = -2**31

SIZE_MAP = {
    "byte": (-128, 127),
    "int": (-2**31, 2**31-1),
    "short": (-32768, 32767),
    "long": (-2**63, 2**63-1),
    "boolean": (0, 1),
    "char": (0, 65535)
}


def get_solution(smt_string):
    proc = subprocess.Popen(args=[PATH_TO_YICES], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    res = proc.communicate(smt_string)[0]
    proc.wait()
    lines = res.split("\n")
    if lines[0] == "unsat":
        return False
    if lines[0] == "sat":
        result_map = {}
        for line in lines[1:]:
            if not line: continue
            eq, var, val = line[1:-1].split()
            result_map[var] = val
        return result_map

def path_constraint_to_solution(constraints, variables):
    constraints = [c for c in constraints if not isinstance(c, bool)]
    smt_string = ["(set-evidence! true)"]
    smt_string += [
        "(define {}::int)".format(variable) for variable in variables
    ] + [
        "(assert (<= {} {}))".format(variable, SIZE_MAP[vtype][1]) for variable, vtype in variables.items()
    ] + [
        "(assert (>= {} {}))".format(variable, SIZE_MAP[vtype][0]) for variable, vtype in variables.items()
    ] + [
        "(assert {})".format(constraint) for constraint in constraints
    ] + ["(check)"]
    return get_solution("\n".join(smt_string))

def solve_constraints(branch_history, constraints, variables):
    j = len(branch_history) - 1
    while j >= 0:
        if not branch_history[j].done:
            branch_history[j] = path.HistoryElement(branch_history[j].branch, not branch_history[j].type,
                                                    branch_history[j].type)
            solve_constraint_params = [
                constraint for id, type, constraint in constraints
            ][:j+1]
            if isinstance(solve_constraint_params[j], bool):
                j -= 1
                continue
            solve_constraint_params[j] = solve_constraint_params[j].negate()
            solution = path_constraint_to_solution(solve_constraint_params, variables)
            if solution:
                return solution, branch_history[:j+1]
        j -= 1
    return True

def update_frontier(branch_history, constraints, variables, error):

    paths = PersistentVariable("paths")
    j = len(branch_history) - 1
    temp = []
    while j >= 0:
        if not branch_history[j].done:
            branch_history[j] = path.HistoryElement(branch_history[j].branch, not branch_history[j].type,
                                                    branch_history[j].type)
            solve_constraint_params = [
                constraint for id, type, constraint in constraints
            ][:j+1]
            if isinstance(solve_constraint_params[j], bool):
                j -= 1
                continue
            solve_constraint_params[j] = solve_constraint_params[j].negate()
            solution = path_constraint_to_solution(solve_constraint_params, variables)
            if solution:
                if tuple(sorted(solution.items())) not in PersistentVariable("inputs").value:
                    temp.append((solution, branch_history[:j+1]))
                # else:
                #     print("discarding", solution)
        j -= 1
    if error:
        paths.value.extend(temp[::-1])  # process nearest branch first
    else:
        paths.value.extendleft(temp[::-1])  # process the faraway ones first



def export_to_input(assignments, filename):
    with open(filename, "w") as f:
        input_file = ["sat"]
        for var, val in assignments.items():
            input_file.append(
                "(= {} {})".format(var, val)
            )
        f.write("\n".join(input_file))

if __name__ == "__main__":
    s = """
(set-evidence! true)
(define x::bool)
(assert (= x false))
(check)
    """
    sol = get_solution(s)