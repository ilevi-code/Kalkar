import re
from dataclasses import dataclass, field, KW_ONLY
from typing import Optional, ClassVar, Union
from position import Position


@dataclass
class Token:
    _: KW_ONLY
    pos: Optional[Position] = field(default=None, compare=False, repr=False)

@dataclass
class Keyword(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(let|return)")

    keyword: str

    def value(self) -> str:
        return self.keyword




@dataclass
class Identifier(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([_\w][_\w\d]*)")

    name: str

    def value(self) -> str:
        return self.name


@dataclass
class Whitespace(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(\s+)")

    spaces: str

    def value(self) -> str:
        return self.spaces


@dataclass
class Seperator(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([\(\);])")

    seperator: str

    def value(self) -> str:
        return self.seperator


@dataclass
class Literal(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(\d+)")

    literal: str

    def value(self) -> str:
        return self.literal


@dataclass
class Operator(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([\+\*-/=])")

    operator: str

    def value(self) -> str:
        return self.operator


TokenKind = Union[Whitespace, Operator, Seperator, Keyword, Literal, Identifier]
