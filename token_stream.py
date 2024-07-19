from tokens import Token
from errors import CompilationError


class EndOfInputError(CompilationError):
    def __init__(self, pos):
        super().__init__(pos, 0, "Unexpected end of input")


class TokenStream:
    def __init__(self, tokens: list):
        self.tokens = tokens
        if len(self.tokens) == 0:
            raise ValueError("Token list is empty")
        self.index = 0

    def peek(self) -> Token:
        try:
            return self.tokens[self.index]
        except IndexError:
            raise EndOfInputError(self.tokens[-1].pos)

    def pop(self) -> Token:
        token = self.peek()
        self.index += 1
        return token

    def is_at_end(self):
        return self.index == len(self.tokens)

    def __len__(self):
        return len(self.index)

    def __repr__(self):
        return f"TokenStream({self.tokens})"
