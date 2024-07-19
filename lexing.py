from typing import List

from position import Position, Line
from errors import CompilationError
from tokens import Token, Identifier, Keyword, Seperator, Literal, Operator, Whitespace
from token_stream import TokenStream


class UnknownCharacher(CompilationError):
    def __init__(self, position: Position):
        unknown = position.line.content[position.start]
        super().__init__(position, f'Unkown character "{unknown}"')


class Tokenizer:
    def tokenize(self, content: str) -> List[Token]:
        tokens = []
        lines = content.split("\n")
        for line_number, line in enumerate(lines, start=1):
            tokens.extend(self.tokenize_line(Line(line, line_number)))
        return TokenStream(tokens)

    @staticmethod
    def tokenize_line(line: Line) -> List[Token]:
        tokens = []
        offset = 0
        while offset < len(line.content):
            token = Tokenizer.token_at(line, offset)
            offset = token.pos.end
            if type(token) is Whitespace:
                continue
            tokens.append(token)
        return tokens

    @staticmethod
    def token_at(line: Line, offset: int) -> Token:
        for cls in [Whitespace, Operator, Seperator, Keyword, Literal, Identifier]:
            match = cls.PATTERN.match(line.content, offset)
            if match is None:
                continue
            position = Position(line, *match.span())
            return cls(match.group(), pos=position)
        raise UnknownCharacher(Position(line, offset, offset + 1))
