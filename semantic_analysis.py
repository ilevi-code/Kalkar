from typing import Dict
from functools import singledispatchmethod

from ast_ import BinaryOperation, UnaryOperation, Assignment, Return, Decleration
from lexing import Identifier, Literal
from errors import CompilationError


class SemanticError(CompilationError):
    pass


class RedelerationError(SemanticError):
    def __init__(self, first_decleration: Identifier, new_decleration: Identifier):
        super().__init__(
            new_decleration.pos, len(new_decleration.name), "Redecleration here"
        )
        self.with_secondary_message_at_token(
            first_decleration, "Previously declared here"
        )
        self.first_decleration = first_decleration
        self.new_decleration = new_decleration


class UndeclaredError(SemanticError):
    def __init__(self, identifier):
        super().__init__(identifier.pos, len(identifier.name), "Undeclared variable")
        self.identifier = identifier


class Variable:
    def __init__(self, identifier):
        self.identifier = identifier


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table: Dict[str, Variable] = {}

    def analyze(self, ast):
        for block in ast:
            self.analyze_once(block)

    @singledispatchmethod
    def analyze_once(self, element):
        raise TypeError(f"No lowering implemented for {type(element)}")

    @analyze_once.register
    def analyze_decleration(self, decleration: Decleration):
        self.analyze_once(decleration.expr)
        self.assert_undeclrated(decleration.identifier)
        self.symbol_table[decleration.identifier.name] = Variable(
            decleration.identifier
        )

    @analyze_once.register
    def analyze_return(self, _return: Return):
        self.analyze_once(_return.expr)

    @analyze_once.register
    def analyze_assignment(self, assignment: Assignment):
        self.analyze_once(assignment.src)
        self.assert_declrated(assignment.dst)

    @analyze_once.register
    def analyze_binary_operation(self, operation: BinaryOperation):
        for operand in [operation.rhs, operation.lhs]:
            self.analyze_once(operand)

    @analyze_once.register
    def analyze_unary_operation(self, operation: UnaryOperation):
        self.analyze_once(operation.operand)

    @analyze_once.register
    def analyze_identifier(self, identifier: Identifier):
        self.assert_declrated(identifier)

    @analyze_once.register
    def analyze_literal(self, _: Literal):
        pass

    def assert_declrated(self, identifier):
        if identifier.name not in self.symbol_table:
            raise UndeclaredError(identifier)

    def assert_undeclrated(self, identifier):
        try:
            previous_decleration = self.symbol_table[identifier.name]
            raise RedelerationError(previous_decleration.identifier, identifier)
        except KeyError:
            pass
