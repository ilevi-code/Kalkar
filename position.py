from dataclasses import dataclass


@dataclass
class Line:
    content: str
    number: int


@dataclass
class Position:
    line: Line
    start: int
    end: int
