import string

from position import Position
from errors import CompilationError


class UnknownCharacher(CompilationError):
    def __init__(self, position: Position):
        unknown = position.line[position.offset]
        super().__init__(position, 1, f'Unkown character "{unknown}"')


class Token:
    def __init__(self, raw: str, pos: Position):
        self.pos = pos
        self.raw = raw

    def __len__(self):
        return len(self.raw)

    def __repr__(self):
        return f"{type(self).__name__}({self.raw})"

    def __eq__(self, other):
        return self.raw == other.raw


class Identifier(Token):
    def __init__(self, name: str, pos: Position = None):
        super().__init__(name, pos)
        self.name = name


class Keyword(Token):
    KEYWORDS = {"return"}

    def __init__(self, keyword: str, pos: Position = None):
        super().__init__(keyword, pos)
        if keyword not in self.KEYWORDS:
            raise ValueError()
        self.keyword = keyword


class Seperator(Token):
    SEPERATORS = set("();")

    def __init__(self, seperator: str, pos: Position = None):
        super().__init__(seperator, pos)
        if seperator not in self.SEPERATORS:
            raise ValueError()
        self.seperator = seperator


class Literal(Token):
    def __init__(self, literal: str, pos: Position = None):
        super().__init__(literal, pos)
        self.literal = int(literal)


class Operator(Token):
    OPERATORS = set("+-*/=")

    def __init__(self, operator: str, pos: Position = None):
        super().__init__(operator, pos)
        if operator not in self.OPERATORS:
            raise ValueError()
        self.operator = operator


class LineScanner:
    SPECIAL = Operator.OPERATORS | Seperator.SEPERATORS

    def __init__(self, line: str, line_number: int):
        self.line = line
        self.index = 0
        self.line_number = line_number

    def is_num(self) -> bool:
        return self.line[self.index].isnumeric()

    def is_special(self) -> bool:
        return self.line[self.index] in self.SPECIAL

    def is_start_of_identifier(self) -> bool:
        return self.line[self.index].isalpha() or self.line[self.index] == "_"

    def is_identifier(self) -> bool:
        return self.is_start_of_identifier() or self.line[self.index].isnumeric()

    def position(self) -> Position:
        return Position(self.line, self.line_number, self.index)

    def read(self) -> str:
        self.skip_spaces()
        start_index = self.index
        try:
            self.advance()
        except IndexError:
            pass
        return self.line[start_index : self.index]

    def skip_spaces(self):
        while self.index < len(self.line) and self.line[self.index].isspace():
            self.index += 1

    def advance(self):
        if self.is_special():
            self.index += 1
        elif self.is_num():
            while self.is_num():
                self.index += 1
        elif self.is_start_of_identifier():
            while self.is_identifier():
                self.index += 1
        else:
            raise UnknownCharacher(self.position())


class Tokenizer:
    def tokenize(self, content: str):
        tokens = []
        lines = content.split("\n")
        for line_number, line in enumerate(lines, start=1):
            line_scanner = LineScanner(line, line_number)
            while lexeme := line_scanner.read():
                for cls in [Operator, Seperator, Keyword, Literal, Identifier]:
                    try:
                        tokens.append(cls(lexeme, line_scanner.position()))
                        break
                    except ValueError:
                        pass
        return tokens
