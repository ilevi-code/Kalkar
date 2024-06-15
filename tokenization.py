import string

from position import Position
from errors import CompilationError
from tokens import Identifier, Keyword, Seperator, Literal, Operator


class UnknownCharacher(CompilationError):
    def __init__(self, position: Position):
        unknown = position.line[position.offset]
        super().__init__(position, 1, f'Unkown character "{unknown}"')



class LineScanner:
    SPECIAL = Operator.OPERATORS | Seperator.SEPERATORS

    def __init__(self, line: str, line_number: int):
        self.line = line
        self.index = 0
        self.line_number = line_number
        self.prev_index = None

    def is_num(self) -> bool:
        return self.line[self.index].isnumeric()

    def is_special(self) -> bool:
        return self.line[self.index] in self.SPECIAL

    def is_start_of_identifier(self) -> bool:
        return self.line[self.index].isalpha() or self.line[self.index] == "_"

    def is_identifier(self) -> bool:
        return self.is_start_of_identifier() or self.line[self.index].isnumeric()

    def is_minus_num(self) -> bool:
        try:
            return self.line[self.index] == '-' and self.line[self.index + 1].isnumeric()
        except IndexError:
            return False

    def last_position(self) -> Position:
        return Position(self.line, self.line_number, self.prev_index)

    def read(self) -> str:
        self.skip_spaces()
        self.prev_index = self.index
        try:
            self.advance()
        except IndexError:
            pass
        return self.line[self.prev_index : self.index]

    def skip_spaces(self):
        while self.index < len(self.line) and self.line[self.index].isspace():
            self.index += 1

    def advance(self):
        if self.is_num() or self.is_minus_num():
            self.index += 1
            while self.is_num():
                self.index += 1
        elif self.is_special():
            self.index += 1
        elif self.is_start_of_identifier():
            while self.is_identifier():
                self.index += 1
        else:
            raise UnknownCharacher(Position(self.line, self.line_number, self.index))


class Tokenizer:
    def tokenize(self, content: str):
        tokens = []
        lines = content.split("\n")
        for line_number, line in enumerate(lines, start=1):
            line_scanner = LineScanner(line, line_number)
            while lexeme := line_scanner.read():
                for cls in [Operator, Seperator, Keyword, Literal, Identifier]:
                    try:
                        tokens.append(cls(lexeme, line_scanner.last_position()))
                        break
                    except ValueError:
                        pass
        return tokens
