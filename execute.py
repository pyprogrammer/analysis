from __future__ import print_function
from textx.metamodel import metamodel_from_file
from solver import update_frontier, export_to_input
from util import PersistentVariable
import nodes
import path
import sys
import os

TRACE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trace.tx")
TARGET_PATH = "/Users/nzhang-dev/Documents/Fall16/CS294-15/cute/hw1/"
PICKLE = os.path.join(TARGET_PATH, "history.pickle")
INPUT = os.path.join(TARGET_PATH, "input")
THRESHOLD = os.environ.get("THRESHOLD", 10)

class Executor(object):

    def __init__(self):
        self.A = {}
        self.metamodel = metamodel_from_file(TRACE_PATH, classes=[
            nodes.Assignment, nodes.Conditional, nodes.SymbolicWrite, nodes.Trace,
            nodes.BinaryOp, nodes.UnaryOp, nodes.Value,
            nodes.Comparison, nodes.UnknownCond
        ])
        self.path = []  # list of (id, then/else, condition)
        self.sym_vars = {}
        self.depth = 0
        self.hist = None

    @staticmethod
    def remove_if_exists(dic, key):
        if key in dic:
            del dic[key]

    def parse(self, filename):
        return self.metamodel.model_from_file(filename)

    def execute(self, trace):
        PersistentVariable("total").value += 1
        branches = PersistentVariable("branches")
        errors = PersistentVariable("errors")
        self.hist = path.read_path(PICKLE)
        if trace.error:
            self.register_error_in_history()
            errors.value += 1

        self.depth = 0
        new_branches = 0
        for line in trace.instructions:
            if isinstance(line, nodes.Assignment):
                self.executeAssignment(line)
            elif isinstance(line, nodes.Conditional):
                self.executeConditional(line)
                if line.id not in branches.value:
                    new_branches += 1
                branches.value.add(line.id)
            elif isinstance(line, nodes.SymbolicWrite):
                self.executeSymbolic(line)
            else:
                raise NotImplementedError()
        # print("inputs:", PersistentVariable("inputs").value)
        update_frontier(self.hist, self.path, self.sym_vars, new_branches > THRESHOLD)
        paths = PersistentVariable("paths")
        completed = PersistentVariable("complete")
        if not paths.value:
            completed.value = True
            sys.exit(1)
        newest_path, newest_history = paths.value.pop()
        export_to_input(newest_path, INPUT)
        PersistentVariable("inputs").value.add(tuple(sorted(newest_path.items())))
        path.write_path(PICKLE, newest_history)

    def executeAssignment(self, line):
        if isinstance(line.rvalue, nodes.Value):
            m1 = line.rvalue.address
            v1 = line.rvalue.value
            m = line.lvalue.address
            if m1 == 0:  # constant
                self.remove_if_exists(self.A, m)
            else:
                if m1 in self.A:
                    self.A[m] = self.A[m1]
                else:
                    self.remove_if_exists(self.A, m)
            return
        elif isinstance(line.rvalue, nodes.BinaryOp):
            left_static = line.rvalue.left.is_static(self.A)
            right_static = line.rvalue.right.is_static(self.A)
            if line.rvalue.op not in {"+", "-", "*", "/", "%"}:
                self.remove_if_exists(self.A, line.lvalue.address)
                return
            elif left_static and right_static:
                self.remove_if_exists(self.A, line.lvalue.address)
                return
            elif left_static:
                self.A[line.lvalue.address] = nodes.BinaryArithmeticOp(
                    line.rvalue.left.value,
                    line.rvalue.op,
                    self.A.get(line.rvalue.right.address, line.rvalue.right.value)
                )
                return
            elif right_static:
                self.A[line.lvalue.address] = nodes.BinaryArithmeticOp(
                    self.A.get(line.rvalue.left.address, line.rvalue.left.value),
                    line.rvalue.op,
                    line.rvalue.right.value
                )
                return
            else:  # Both symbolic
                if line.rvalue.op == "*":
                    # concretize first
                    self.A[line.lvalue.address] = nodes.BinaryArithmeticOp(
                        line.rvalue.left.value,
                        line.rvalue.op,
                        self.A.get(line.rvalue.right.address, line.rvalue.right.value)
                    )
                    return
                elif line.rvalue.op in ("-", "+"):
                    self.A[line.lvalue.address] = nodes.BinaryArithmeticOp(
                        self.A.get(line.rvalue.left.address, line.rvalue.left.value),
                        line.rvalue.op,
                        self.A.get(line.rvalue.right.address, line.rvalue.right.value)
                    )
                    return

                elif line.rvalue.op in ("%", "/"):  # concretize right side
                    self.A[line.lvalue.address] = nodes.BinaryArithmeticOp(
                        self.A.get(line.rvalue.left.address, line.rvalue.left.value),
                        line.rvalue.op,
                        line.rvalue.right.value
                    )
                    return


        print(line.rvalue)
        raise NotImplementedError()

    def executeSymbolic(self, line):
        self.A[line.address] = nodes.Symbol(line.var)
        self.sym_vars[line.var] = line.type

    def executeConditional(self, line):
        if line.val in (True, False):
            cond = True
        elif not line.val.is_recognized():  # custom operator
            cond = True
        elif line.val.left.address not in self.A and line.val.right.address not in self.A:
            # purely concrete
            cond = True
        else:
            if line.btype == "then":
                cond = line.val
            else:
                cond = line.val.negate()
            if cond.left.address in self.A:
                cond.left = self.A[cond.left.address]
            if cond.right.address in self.A:
                cond.right = self.A[cond.right.address]
        self.path.append(
            (line.id, line.btype, cond)
        )
        path.cmp_n_set_branch_hist(self.hist, line.id, line.btype == "then", self.depth)
        self.depth += 1

    @staticmethod
    def create_history():
        with open(os.path.join(TARGET_PATH, "history.log"), "a") as history:
            print("Start run", file=history)

    @staticmethod
    def register_error_in_history():
        with open(os.path.join(TARGET_PATH, "history.log"), "a") as history:
            print("ERROR:", file=history)
            try:
                with open(INPUT) as inputs:
                    for line in inputs:
                        print(line, file=history)
            except IOError:
                print("Default Inputs")
            print(file=history)

    @staticmethod
    def is_new_run():
        return not os.path.isfile(PICKLE)


if __name__ == "__main__":
    try:
        execute = Executor()
        parsed = execute.parse(os.path.join(TARGET_PATH, "trace"))
        execute.execute(parsed)
    except ValueError:
        print("ERROR on Path Prediction" + "+" * 40, file=sys.stderr)
        path.write_path(PICKLE, [])
