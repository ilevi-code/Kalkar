from tokenization import Identifier, Literal, Operator, Seperator, Keyword
from errors import CompilationError


class UnexpectedTokenError(CompilationError):
    def __init__(self, token):
        super().__init__(
            token.pos, len(token.raw), f'Expected expression before "{token.raw}"'
        )


class ExpectedTokenError(CompilationError):
    def __init__(self, token, expected):
        super().__init__(
            token.pos, len(token.raw), f'Expected {expected} before "{token.raw}"'
        )


class EndOfInputError(CompilationError):
    def __init__(self, pos):
        super().__init__(pos, 0, f"Unexpected and of input")


class Operation:
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
        if type(self.lhs) is Operation and self.lhs.order < self.order:
            new_root = self.lhs
            self.lhs = new_root.rhs
            new_root.rhs = self
            return new_root
        if type(self.rhs) is Operation and self.rhs.order < self.order:
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


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0
        self.tree = []

    def parse(self):
        parsed = []
        while self.index < len(self.tokens):
            if type(self.current_token) is Identifier:
                parsed.append(self.parse_assignment())
            elif type(self.current_token) is Keyword:
                parse.append(self.parse_return_statment())
            else:
                raise UnexpectedTokenError(self.current_token)
        return parsed

    def parse_assignment(self):
        dest = self.tokens[self.index]
        self.index += 1
        if (
            type(self.current_token) is not Operator
            or self.current_token.operator != "="
        ):
            raise ExpectedTokenError(self.current_token, "=")
        self.index += 1
        src = self.parse_expression()
        return Assignment(dest, src)

    def parse_expression(self):
        root = self.parse_operand()

        while True:
            if type(self.current_token) is Seperator:
                break
            elif type(self.current_token) is Operator:
                operator = self.current_token
                self.index += 1
                rhs = self.parse_operand()
                root = Operation(root, operator, rhs)
                root = root.reorder()
            else:
                raise ExpectedTokenError(self.current_token, ";")
        return root

    def parse_operand(self):
        if type(self.current_token) in [Literal, Identifier]:
            operand = self.current_token
            self.index += 1
            return operand
        elif (
            type(self.current_token) is Seperator
            and self.current_token.seperator == "("
        ):
            self.index += 1
            expression = self.parse_expression()
            if (
                type(self.current_token) is not Seperator
                or self.current_token.seperator != ")"
            ):
                raise ExpectedTokenError(self.current_token, ")")
            self.index += 1
            if type(expression) is Operation:
                return expression.parenthesize()
            return expression
        else:
            raise UnexpectedTokenError(self.current_token)

    @property
    def current_token(self):
        try:
            return self.tokens[self.index]
        except IndexError:
            if len(self.tokens) == 0:
                raise EndOfInputError(Position("", 1, 1))
            raise EndOfInputError(self.tokens[-1].pos)
