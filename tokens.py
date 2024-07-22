import re
from dataclasses import dataclass, field
from typing import Optional, ClassVar, Union
from position import Position


@dataclass
class Token:
    value: str
    pos: Optional[Position] = field(default=None, compare=False, repr=False)


@dataclass
class Keyword(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(let|return)")


@dataclass
class Identifier(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([_\w][_\w\d]*)")


@dataclass
class Whitespace(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(\s+)")


@dataclass
class Seperator(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([\(\);])")


@dataclass
class Literal(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"(\d+)")


@dataclass
class Operator(Token):
    PATTERN: ClassVar[re.Pattern] = re.compile(r"([\+\*-/=])")


TokenKind = Union[Whitespace, Operator, Seperator, Keyword, Literal, Identifier]
