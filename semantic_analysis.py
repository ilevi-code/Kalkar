from typing import Dict
from functools import singledispatchmethod

from ast_ import BinaryOperation, UnaryOperation, Assignment, Return, Decleration
from lexing import Identifier, Literal
from errors import CompilationError


class SemanticError(CompilationError):
    pass


class RedelerationError(SemanticError):
    def __init__(self, first_decleration: Identifier, new_decleration: Identifier):
        super().__init__(new_decleration.pos, "Redecleration here")
        self.with_secondary_message_at_token(
            first_decleration, "Previously declared here"
        )
        self.first_decleration = first_decleration
        self.new_decleration = new_decleration


class UndeclaredError(SemanticError):
    def __init__(self, identifier):
        super().__init__(identifier.pos, "Undeclared variable")
        self.identifier = identifier


class ConstAssignmentError(SemanticError):
    def __init__(self, first_decleration: Identifier, usage: Identifier):
        super().__init__(usage.pos, "Cannot assign to const")
        self.with_secondary_message_at_token(first_decleration, "Declared 'const' here")
        self.first_decleration = first_decleration
        self.usage = usage


class Variable:
    def __init__(self, identifier, is_const=False):
        self.identifier = identifier
        self.is_const = is_const


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
        self.assert_undeclared(decleration.identifier)
        self.symbol_table[decleration.identifier.value] = Variable(
            decleration.identifier,
            decleration.is_const,
        )

    @analyze_once.register
    def analyze_return(self, _return: Return):
        self.analyze_once(_return.expr)

    @analyze_once.register
    def analyze_assignment(self, assignment: Assignment):
        self.analyze_once(assignment.src)
        self.assert_declared(assignment.dst)
        self.assert_mutable(assignment.dst)

    @analyze_once.register
    def analyze_binary_operation(self, operation: BinaryOperation):
        for operand in [operation.rhs, operation.lhs]:
            self.analyze_once(operand)

    @analyze_once.register
    def analyze_unary_operation(self, operation: UnaryOperation):
        self.analyze_once(operation.operand)

    @analyze_once.register
    def analyze_identifier(self, identifier: Identifier):
        self.assert_declared(identifier)

    @analyze_once.register
    def analyze_literal(self, _: Literal):
        pass

    def assert_declared(self, identifier):
        if identifier.value not in self.symbol_table:
            raise UndeclaredError(identifier)

    def assert_undeclared(self, identifier):
        try:
            previous_decleration = self.symbol_table[identifier.value]
            raise RedelerationError(previous_decleration.identifier, identifier)
        except KeyError:
            pass

    def assert_mutable(self, identifier: Identifier):
        previous_decleration = self.symbol_table[identifier.value]
        if previous_decleration.is_const:
            raise ConstAssignmentError(previous_decleration.identifier, identifier)
