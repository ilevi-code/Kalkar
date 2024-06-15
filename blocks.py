from tokenization import Operator

class Expression:
    ORDER_OF_OPERATIONS = {
        "(": 3,
        "*": 2,
        "/": 2,
        "+": 1,
        "-": 1,
    }

    def __init__(self, lhs, operator, rhs):
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs
        self.order = self.ORDER_OF_OPERATIONS[operator.operator]

    def parenthesize(self):
        self.order = self.ORDER_OF_OPERATIONS["("]
        return self

    def reorder(self):
        if type(self.lhs) is Expression and self.lhs.order < self.order:
            new_root = self.lhs
            self.lhs = new_root.rhs
            new_root.rhs = self
            return new_root
        if type(self.rhs) is Expression and self.rhs.order < self.order:
            new_root = self.rhs
            self.rhs = new_root.lhs
            new_root.lhs = self
            return new_root
        return self

    def __eq__(self, other):
        return (
            self.lhs == other.lhs
            and self.operator == other.operator
            and self.rhs == other.rhs
            and self.order == other.order
        )

    def __str__(self):
        return f"<order={self.order}, {self.lhs} {self.operator} {self.rhs}>"


class Assignment:
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def __eq__(self, other):
        return self.dst == other.dst and self.src == other.src


class Return:
    def __init__(self, expr):
        self.expr = expr

    def __eq__(self, other):
        return self.expr == other.expr
