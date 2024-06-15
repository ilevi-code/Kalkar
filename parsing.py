from tokenization import Identifier, Literal, Operator, Seperator, Keyword
from errors import CompilationError


class UnexpectedTokenError(CompilationError):
    def __init__(self, token):
        super().__init__(
            token.pos, len(token.raw), f'Unexpected expression "{token.raw}"'
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

    def __eq__(self, other):
        return (
            self.lhs == other.lhs
            and self.operator == other.operator
            and self.rhs == other.rhs
        )

    def __str__(self):
        return f"{self.lhs} {self.operator} {self.rhs}"


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
            raise ExpectedTokenError(next_token, "=")
        self.index += 1
        src = self.parse_expression()
        return Assignment(dest, src)

    def parse_expression(self):
        lhs = self.parse_operand()

        if type(self.current_token) is Seperator:
            return lhs
        elif type(self.current_token) is Operator:
            operator = self.current_token
            self.index += 1
            rhs = self.parse_operand()
            operation = Operation(lhs, operator, rhs)
            return self.reorder_opreation(operation)
        else:
            raise ExpectedTokenError(self.current_token, ";")

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
                expression.parenthesize()
            return expression
        else:
            raise UnexpectedTokenError(self.current_token)

    def reorder_opreation(self, operation):
        # TODO
        return operation

    @property
    def current_token(self):
        try:
            return self.tokens[self.index]
        except IndexError:
            if len(self.tokens) == 0:
                raise EndOfInputError(Position("", 1, 1))
            raise EndOfInputError(self.tokens[-1].pos)
