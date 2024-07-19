import re
from dataclasses import dataclass, field, KW_ONLY
from typing import Optional, ClassVar, Union
from position import Position


@dataclass
class Token:
    _: KW_ONLY
    pos: Optional[Position] = field(default=None, compare=False, repr=False)

    def value(self) -> str:
        return self.pos.line.content[self.pos.start : self.pos.end]


@dataclass
class Keyword(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(let|return)")

    keyword: str


@dataclass
class Identifier(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([_\w][_\w\d]*)")

    name: str


@dataclass
class Whitespace(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(\s+)")

    spaces: str


@dataclass
class Seperator(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([\(\);])")

    seperator: str


@dataclass
class Literal(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(\d+)")

    literal: str


@dataclass
class Operator(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([\+\*-/=])")

    operator: str


TokenKind = Union[Whitespace, Operator, Seperator, Keyword, Literal, Identifier]
