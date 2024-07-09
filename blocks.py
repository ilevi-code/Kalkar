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


class UnaryOperation:
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __eq__(self, other):
        return self.operator == other.operator and self.operand == other.operand


class Decleration:
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    def __eq__(self, other):
        return self.identifier == other.identifier and self.expr == other.expr


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
