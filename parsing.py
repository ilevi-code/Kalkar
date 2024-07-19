from functools import singledispatchmethod

from tokens import Identifier, Literal, Operator, Seperator, Keyword, Whitespace
from token_stream import TokenStream
from errors import CompilationError
from ast_ import BinaryOperation, UnaryOperation, Assignment, Return, Decleration


class UnexpectedTokenError(CompilationError):
    def __init__(self, token):
        super().__init__(token.pos, f'Expected expression before "{token.value()}"')


class ExpectedTokenError(CompilationError):
    def __init__(self, token, expected):
        super().__init__(token.pos, f'Expected {expected} before "{token.value()}"')


class Parser:
    def parse(self, tokens: TokenStream):
        parsed = []
        while not tokens.is_at_end():
            token = tokens.pop()
            ast_element = self.parse_token(token, tokens)
            if ast_element is not None:
                parsed.append(ast_element)
        return parsed

    @staticmethod
    def filter_tokens(tokens: TokenStream) -> TokenStream:
        filtered = []
        for token in tokens.tokens:
            if type(token) is Whitespace:
                filtered.append(token)
        return TokenStream(filtered)

    @singledispatchmethod
    def parse_token(self, token, tokens: TokenStream):
        raise UnexpectedTokenError(token)

    @parse_token.register
    def parse_whitespace(self, _: Whitespace, toekns: TokenStream):
        pass

    @parse_token.register
    def parse_assignment(self, dest: Identifier, tokens: TokenStream):
        maybe_operator = tokens.pop()
        if type(maybe_operator) is not Operator or maybe_operator.operator != "=":
            raise ExpectedTokenError(maybe_operator, "=")
        src = self.parse_expression(tokens)
        return Assignment(dest, src)

    def parse_expression(self, tokens):
        return self.parse_expression_until_seperator(tokens, ";")

    def parse_expression_until_seperator(self, tokens, seperator):
        root = self.parse_operand(tokens)

        while True:
            token = tokens.pop()
            if type(token) is Seperator:
                if token.seperator == seperator:
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

    def parse_operand(self, tokens):
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
        expression = self.parse_expression_until_seperator(tokens, ")")
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

    def parse_return(self, tokens):
        expr = self.parse_expression(tokens)
        return Return(expr)

    def parse_decleration(self, tokens):
        maybe_identifier = tokens.pop()
        if type(maybe_identifier) is not Identifier:
            raise ExpectedTokenError(maybe_identifier, "identifier")
        maybe_equal_sign = tokens.pop()
        if type(maybe_equal_sign) is not Operator or maybe_equal_sign.operator != "=":
            raise ExpectedTokenError(maybe_equal_sign, "=")
        expression = self.parse_expression(tokens)
        return Decleration(maybe_identifier, expression)

    @staticmethod
    def encforce_order_of_operation(root):
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
