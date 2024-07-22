from functools import singledispatchmethod

from tokens import TokenKind, Identifier, Literal, Operator, Seperator, Keyword
from token_stream import TokenStream
from errors import CompilationError
from ast_ import BinaryOperation, UnaryOperation, Assignment, Return, Decleration


class UnexpectedTokenError(CompilationError):
    def __init__(self, token):
        super().__init__(token.pos, f'Expected expression before "{token.value()}"')


class ExpectedTokenError(CompilationError):
    def __init__(self, unexpected: TokenKind, expected: TokenKind):
        super().__init__(unexpected.pos, f'Expected {expected.value()} before "{unexpected.value()}"')
        self.expected = expected
        self.unexpected = unexpected


class Parser:
    def parse(self, tokens: TokenStream):
        parsed = []
        while not tokens.is_at_end():
            token = tokens.pop()
            ast_element = self.parse_token(token, tokens)
            parsed.append(ast_element)
        return parsed

    @singledispatchmethod
    def parse_token(self, token, tokens: TokenStream):
        raise UnexpectedTokenError(token)

    @parse_token.register
    def parse_assignment(self, dest: Identifier, tokens: TokenStream):
        maybe_operator = tokens.pop()
        if maybe_operator != Operator("="):
            raise ExpectedTokenError(maybe_operator, "=")
        src = self.parse_expression(tokens)
        return Assignment(dest, src)

    def parse_expression(self, tokens: TokenStream):
        return self.parse_expression_until_seperator(tokens, Seperator(";"))

    def parse_expression_until_seperator(self, tokens: TokenStream, seperator: Seperator):
        root = self.parse_operand(tokens)

        while True:
            token = tokens.pop()
            if type(token) is Seperator:
                if token == seperator:
                    break
                else:
                    raise ExpectedTokenError(token, seperator)
            elif type(token) is Operator:
                operator = token
                rhs = self.parse_operand(tokens)
                root = BinaryOperation(root, operator, rhs)
                root = Parser.encforce_order_of_operation(root)
            else:
                raise ExpectedTokenError(token, seperator)
        return root

    def parse_operand(self, tokens: TokenStream):
        token = tokens.pop()
        return self._parse_operand(token, tokens)

    @singledispatchmethod
    def _parse_operand(self, token, tokens: TokenStream):
        raise UnexpectedTokenError(token)

    @_parse_operand.register
    def _(self, operator: Operator, tokens: TokenStream):
        if operator.operator == "-":
            operand = self.parse_operand(tokens)
            return UnaryOperation(operator, operand)
        else:
            raise UnexpectedTokenError(operator)

    @_parse_operand.register(Identifier)
    @_parse_operand.register(Literal)
    def _(self, token, tokens: TokenStream):
        return token

    @_parse_operand.register
    def _(self, seperator: Seperator, tokens: TokenStream):
        if seperator.seperator != "(":
            raise UnexpectedTokenError(seperator)
        expression = self.parse_expression_until_seperator(tokens, Seperator(")"))
        if type(expression) is BinaryOperation:
            return expression.parenthesize()
        return expression

    @parse_token.register
    def parse_keyword(self, keyword: Keyword, tokens: TokenStream):
        parsers = {
            "return": self.parse_return,
            "let": self.parse_decleration,
        }
        try:
            return parsers[keyword.keyword](tokens)
        except KeyError:
            raise CompilationError(
                keyword.pos, len(keyword.keyword), "Unsupported keyword"
            )

    def parse_return(self, tokens: TokenStream):
        expr = self.parse_expression(tokens)
        return Return(expr)

    def parse_decleration(self, tokens: TokenStream):
        maybe_identifier = tokens.pop()
        if type(maybe_identifier) is not Identifier:
            raise ExpectedTokenError(maybe_identifier, "identifier")
        maybe_equal_sign = tokens.pop()
        if maybe_equal_sign != Operator("="):
            raise ExpectedTokenError(maybe_equal_sign, "=")
        expression = self.parse_expression(tokens)
        return Decleration(maybe_identifier, expression)

    @staticmethod
    def encforce_order_of_operation(root: BinaryOperation):
        if type(root.lhs) is BinaryOperation and root.is_lower_order(root.lhs):
            new_root = root.lhs
            root.lhs = new_root.rhs
            new_root.rhs = root
            return new_root
        if type(root.rhs) is BinaryOperation and root.is_lower_order(root.rhs):
            new_root = root.rhs
            root.rhs = new_root.lhs
            new_root.lhs = root
            return new_root
        return root
