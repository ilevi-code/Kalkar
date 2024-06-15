from tokenization import Identifier, Literal, Operator, Seperator, Keyword
from errors import CompilationError
from blocks import Operation, Assignment


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


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.index = 0

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
