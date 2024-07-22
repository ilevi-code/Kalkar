from functools import singledispatchmethod

from tokens import Literal, Identifier
import ast_ as ast
from ir import LoadConstant, LoadVariable, UnaryOperation, BinaryOperation, Return


class LoweringPass:
    def __init__(self):
        self.ir = []
        self.temporaries_count = 0

    def lower(self, ast: list):
        for node in ast:
            self.lower_once(node)
        return self.ir

    @singledispatchmethod
    def lower_once(self, node):
        raise TypeError(f"No lowering implemented for {type(node)}")

    @lower_once.register
    def _(self, statement: ast.Decleration):
        var = self.lower_once(statement.expr)
        self.ir.append(LoadVariable(statement.identifier.value, var))

    @lower_once.register
    def _(self, statement: ast.Assignment):
        var = self.lower_once(statement.src)
        self.ir.append(LoadVariable(statement.dst.value, var))

    @lower_once.register
    def _(self, statement: ast.Return):
        self.ir.append(Return(self.lower_once(statement.expr)))

    @lower_once.register
    def _(self, unary_op: ast.UnaryOperation):
        var = self.lower_once(unary_op.operand)
        self.ir.append(UnaryOperation(unary_op.operator.value, var))
        return var

    @lower_once.register
    def _(self, binary_op: ast.BinaryOperation):
        rhs = self.lower_once(binary_op.rhs)
        lhs = self.lower_once(binary_op.lhs)
        dest = self.new_temp_var()
        self.ir.append(BinaryOperation(dest, binary_op.operator.value, lhs, rhs))
        return dest

    @lower_once.register
    def _(self, literal: Literal):
        var_name = self.new_temp_var()
        self.ir.append(LoadConstant(var_name, int(literal.value)))
        return var_name

    @lower_once.register
    def _(self, identifier: Identifier):
        return identifier.value

    def new_temp_var(self) -> str:
        old_count = self.temporaries_count
        self.temporaries_count += 1
        # Uniqeness guaranteed
        # The percent-sign is not a valid prefix for user defined variables
        return f"%{old_count}"
