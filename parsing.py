from tokens import Identifier, Literal, Operator, Seperator, Keyword
from errors import CompilationError
from ast_ import BinaryOperation, UnaryOperation, Assignment, Return, Decleration


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


class Parser:
    def parse(self, tokens):
        parsed = []
        while not tokens.is_at_end():
            if type(tokens.peek()) is Identifier:
                parsed.append(self.parse_assignment(tokens))
            elif type(tokens.peek()) is Keyword:
                parsed.append(self.parse_keyword(tokens))
            else:
                raise UnexpectedTokenError(tokens.peek())
        return parsed

    def parse_assignment(self, tokens):
        dest = tokens.pop()
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
            curr = tokens.pop()
            if type(curr) is Seperator:
                if curr.seperator == seperator:
                    break
                else:
                    raise ExpectedTokenError(curr, seperator)
            elif type(curr) is Operator:
                operator = curr
                rhs = self.parse_operand(tokens)
                root = BinaryOperation(root, operator, rhs)
                root = Parser.encforce_order_of_operation(root)
            else:
                raise ExpectedTokenError(curr, seperator)
        return root

    def parse_operand(self, tokens):
        curr = tokens.pop()
        if type(curr) is Operator and curr.operator == "-":
            operator = curr
            operand = self.parse_operand(tokens)
            return UnaryOperation(operator, operand)
        if type(curr) in [Literal, Identifier]:
            return curr
        elif type(curr) is Seperator and curr.seperator == "(":
            expression = self.parse_expression_until_seperator(tokens, ")")
            if type(expression) is BinaryOperation:
                return expression.parenthesize()
            return expression
        else:
            raise UnexpectedTokenError(curr)

    def parse_keyword(self, tokens):
        keyword = tokens.pop()
        if keyword.keyword == "return":
            return self.parse_return(tokens)
        if keyword.keyword == "let":
            return self.parse_decleration(tokens)
        assert False, f"unsupported keyword {keyword.keyword}"

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
