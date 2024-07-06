from blocks import BinaryOperation, Assignment, Return
from lexing import Identifier
from errors import CompilationError

TYPE_ANALYZERS = {}


def type_analyzer(_type):
    def _inner_decorator(func):
        TYPE_ANALYZERS[_type] = func
        return func
    return _inner_decorator


class SemanticError(CompilationError):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.existing_variables = set()

    def analyze(self, ast):
        for block in ast:
            self.analyze_type(block)

    def analyze_type(self, element):
        try:
            analyzer = TYPE_ANALYZERS[type(element)]
        except KeyError:
            return
        analyzer(self, element)

    @type_analyzer(Return)
    def analyze_return(self, assignment):
        self.analyze_type(assignment.expr)

    @type_analyzer(Assignment)
    def analyze_assignment(self, assignment):
        self.analyze_type(assignment.src)

    @type_analyzer(BinaryOperation)
    def analyze_binary_operation(self, block):
        for operand in [block.rhs, block.lhs]:
            self.analyze_type(operand)

    @type_analyzer(Identifier)
    def analyze_identifier(self, identifier):
        if identifier.name not in self.existing_variables:
            raise SemanticError(identifier.pos, len(identifier.name), "Undeclared variable")
