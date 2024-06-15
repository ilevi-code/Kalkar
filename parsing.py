from tokenization import Identifier, Literal, Operator, Seperator, Keyword
from errors import CompilationError
from blocks import Expression, Assignment, Return


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
                parsed.append(self.parse_keyword())
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
                if self.current_token.seperator == ";":
                    self.index += 1
                break
            elif type(self.current_token) is Operator:
                operator = self.current_token
                self.index += 1
                rhs = self.parse_operand()
                root = Expression(root, operator, rhs)
                root = root.reorder()
            else:
                raise ExpectedTokenError(self.current_token, ";")
        return root

    def parse_operand(self):
        if type(self.current_token) is Operator and self.current_token.operator == '-' and \
            self.index < len(self.tokens) and type(self.tokens[self.index + 1]) is Literal:
            after = self.tokens[self.index + 1]
            after.literal = -after.literal
            after.raw = "-" + after.raw
            self.index += 2
            return after
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
            self.check_matching_parenthesis()
            if type(expression) is Expression:
                return expression.parenthesize()
            return expression
        else:
            raise UnexpectedTokenError(self.current_token)

    def check_matching_parenthesis(self):
        is_end = self.index >= len(self.tokens)
        if is_end:
            raise ExpectedTokenError(self.tokens[-1], ")")
        if (
            type(self.current_token) is not Seperator
            or self.current_token.seperator != ")"
        ):
            raise ExpectedTokenError(self.current_token, ")")
        self.index += 1

    def parse_keyword(self):
        keyword = self.current_token
        self.index += 1
        if keyword.keyword == "return":
            expr = self.parse_expression()
            return Return(expr)
        assert False, f"unsupported keyword {keyword.keyword}"

    @property
    def current_token(self):
        try:
            return self.tokens[self.index]
        except IndexError:
            if len(self.tokens) == 0:
                raise EndOfInputError(Position("", 1, 1))
            raise EndOfInputError(self.tokens[-1].pos)
