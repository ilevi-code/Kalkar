from __future__ import annotations
from typing import ClassVar, Dict, Union
from dataclasses import dataclass

from tokens import Operator, Identifier, Literal


@dataclass
class BinaryOperation:
    lhs: Expression
    operator: Operator
    rhs: Expression
    order: bool = False
    is_parenthseized: bool = False

    ORDER_OF_OPERATIONS: ClassVar[Dict[str, int]] = {
        "*": 2,
        "/": 2,
        "+": 1,
        "-": 1,
    }

    def __post_init__(self):
        self.order = BinaryOperation.ORDER_OF_OPERATIONS[self.operator.value]

    def is_lower_order(self, other):
        return other.order < self.order and not other.is_parenthseized

    def parenthesize(self):
        self.is_parenthseized = True
        return self


@dataclass
class UnaryOperation:
    operator: Operator
    operand: Expression


@dataclass
class Decleration:
    identifier: Identifier
    expr: Expression


@dataclass
class Assignment:
    dst: Identifier
    src: Expression


@dataclass
class Return:
    expr: Expression


Expression = Union[Identifier, Literal, UnaryOperation, BinaryOperation]
