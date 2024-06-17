from tokenization import Operator

class BinaryOperation:
    ORDER_OF_OPERATIONS = {
        "*": 2,
        "/": 2,
        "+": 1,
        "-": 1,
    }

    def __init__(self, lhs, operator, rhs):
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs
        self.order = BinaryOperation.ORDER_OF_OPERATIONS[operator.operator]
        self.is_parenthseized = False

    def is_lower_order(self, other):
        return other.order < self.order and not other.is_parenthseized

    def parenthesize(self):
        self.is_parenthseized = True
        return self

    def reorder(self):
        if type(self.lhs) is BinaryOperation and self.is_lower_order(self.lhs):
            new_root = self.lhs
            self.lhs = new_root.rhs
            new_root.rhs = self
            return new_root
        if type(self.rhs) is BinaryOperation and self.is_lower_order(self.rhs):
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
            and self.is_parenthseized == other.is_parenthseized
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
