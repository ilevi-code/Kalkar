from typing import Dict

from blocks import BinaryOperation, UnaryOperation, Assignment, Return, Decleration
from lexing import Identifier, Literal
from errors import CompilationError

TYPE_ANALYZERS = {}


def type_analyzer(_type):
    def _inner_decorator(func):
        TYPE_ANALYZERS[_type] = func
        return func

    return _inner_decorator


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


class SemanticAnalyzer:
    def __init__(self):
        self.existing_variables: Dict[str, Identifier] = {}

    def analyze(self, ast):
        for block in ast:
            self.analyze_once(block)

    def analyze_once(self, element):
        analyzer = TYPE_ANALYZERS[type(element)]
        analyzer(self, element)

    @type_analyzer(Decleration)
    def analyze_decleration(self, decleration):
        self.analyze_once(decleration.expr)
        self.assert_undeclrated(decleration.identifier)
        self.existing_variables[decleration.identifier.name] = decleration.identifier

    @type_analyzer(Return)
    def analyze_return(self, assignment):
        self.analyze_once(assignment.expr)

    @type_analyzer(Assignment)
    def analyze_assignment(self, assignment):
        self.analyze_once(assignment.src)
        self.assert_declrated(assignment.dst)

    @type_analyzer(BinaryOperation)
    def analyze_binary_operation(self, operation):
        for operand in [operation.rhs, operation.lhs]:
            self.analyze_once(operand)

    @type_analyzer(UnaryOperation)
    def analyze_unary_operation(self, operation):
        self.analyze_once(operation.operand)

    @type_analyzer(Identifier)
    def analyze_identifier(self, identifier):
        self.assert_declrated(identifier)

    @type_analyzer(Literal)
    def analyze_literal(self, _):
        pass

    def assert_declrated(self, identifier):
        if identifier.name not in self.existing_variables:
            raise UndeclaredError(identifier)

    def assert_undeclrated(self, identifier):
        try:
            previous_decleration = self.existing_variables[identifier.name]
            raise RedelerationError(previous_decleration, identifier)
        except KeyError:
            pass
