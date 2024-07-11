from dataclasses import dataclass


@dataclass
class LoadConstant:
    dest: str
    value: int


@dataclass
class LoadVariable:
    dest: str
    source: str


@dataclass
class UnaryOperation:
    op: str
    var: str


@dataclass
class BinaryOperation:
    dest: str
    op: str
    lhs: str
    rhs: str


@dataclass
class Return:
    var: str
