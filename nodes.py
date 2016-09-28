import ast


class CuteAstNode(ast.AST):
    pass

class Trace(CuteAstNode):
    _fields = ["instructions", "error", "parent"]

class SymbolicWrite(CuteAstNode):
    _fields = ["address", "type", "var", "parent"]

class Assignment(CuteAstNode):
    _fields = ["lvalue", "rvalue", "parent"]

class Conditional(CuteAstNode):
    _fields = ["btype", "id", "val", "parent"]

class Value(CuteAstNode):
    _fields = ["address", "value", "parent"]

    def is_static(self, memory):
        if self.address == 0:
            return True
        if self.address not in memory:
            return True
        return False

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class BinaryOp(CuteAstNode):
    _fields = ["left", "right", "op", "parent"]

class UnaryOp(CuteAstNode):
    _fields = ["op", "val", "parent"]


class MathNode(ast.AST):
    pass

class Symbol(MathNode):
    _fields = ["sym"]

    def __str__(self):
        return self.sym

    def __repr__(self):
        return "Symbol({})".format(self.sym)

class BinaryArithmeticOp(MathNode):
    _fields = ["left", "op", "right"]
    def __str__(self):
        return "({} {} {})".format(self.op, self.left, self.right)

    def __repr__(self):
        return "BinaryArithmeticOp({}, {}, {})".format(self.op, self.left, self.right)

class ConditionNode(ast.AST):
    OPERATOR_INVERSES = {
        "<": ">=",
        "<=": ">",
        "==": "!=",
        "!=": "==",
        ">=": "<",
        ">": "<="
    }

    OPERATOR_TO_YICES = {
        "==": "=",
        "!=": "/="
    }

class Comparison(ConditionNode):
    _fields = ["left", "op", "right"]

    def negate(self):
        return Comparison(
            self.left,
            self.OPERATOR_INVERSES[self.op],
            self.right
        )

    def is_recognized(self):
        return self.op in self.OPERATOR_INVERSES

    def __str__(self):
        op = self.OPERATOR_TO_YICES.get(self.op, self.op)
        return "({} {} {})".format(op, self.left, self.right)

    def __repr__(self):
        return "Comparison" + str(self)

class UnknownCond(ConditionNode):
    _fields = ["op", "val"]
    def is_recognized(self):
        return False
