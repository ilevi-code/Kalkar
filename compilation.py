from blocks import BinaryOperation, UnaryOperation, Assignment, Return, Decleration
from tokens import Identifier, Literal


class Compiler:
    STACK_ALIGNMENT = 0x10
    PROLOGUE = [
        ".global main",
        "main:",
        "push %rbp",
        "mov  %rsp, %rbp",
    ]
    EPILOGUE = [
        ".section .rodata",
        "format:",
        '.asciz "%d\\n"',
    ]

    def __init__(self):
        self.output = []
        self.stack_positions = {}
        self.stack_top = 0

    def compile(self, blocks):
        for block in blocks:
            if type(block) is Return:
                self.compile_return(block)
            elif type(block) is Assignment:
                self.compile_assignment(block)
            elif type(block) is Decleration:
                self.compile_decleration(block)
            else:
                assert False, f"Unknown expression {block}"
        self.align_stack()
        total = self.PROLOGUE.copy()
        if self.stack_top != 0:
            total.append(f"sub ${self.stack_top}, %rsp")
        total.extend(self.output)
        total.extend(self.EPILOGUE)
        return total

    def align_stack(self):
        self.stack_top = (self.stack_top + (self.STACK_ALIGNMENT - 1)) & ~(
            self.STACK_ALIGNMENT - 1
        )

    def compile_return(self, statement):
        if type(statement.expr) is Literal:
            self.compile_literal(statement.expr)
        elif type(statement.expr) is Identifier:
            self.compile_identifier(statement.expr)
        elif type(statement.expr) is UnaryOperation:
            self.compile_unary_operation(statement.expr)
        elif type(statement.expr) is BinaryOperation:
            self.compile_binary_operation(statement.expr)
        else:
            assert False, f"Unknown expression {statement.expr}"
        self.output.extend(
            [
                "mov %rax, %rsi",
                "lea  format(%rip), %rdi",
                "call printf",
                "mov %rbp, %rsp",
                "pop %rbp",
                "mov $0, %rax",
                "ret",
            ]
        )

    def compile_binary_operation(self, operation, is_rhs=False):
        if is_rhs:
            self.output.append("push %rax")
        for operand, is_operand_rhs in [(operation.lhs, False), (operation.rhs, True)]:
            if type(operand) is Literal:
                self.compile_literal(operand, is_operand_rhs)
            elif type(operand) is Identifier:
                self.compile_identifier(operand, is_operand_rhs)
            elif type(operand) is UnaryOperation:
                self.compile_unary_operation(operand, is_operand_rhs)
            elif type(operand) is BinaryOperation:
                self.compile_binary_operation(operand, is_operand_rhs)
            else:
                assert False, f"Unknown expression {operation.expr}"
        self.compile_binary_operator(operation.operator)
        if is_rhs:
            self.output.append("mov %rax, %rbx")
            self.output.append("pop %rax")

    def compile_literal(self, literal, is_rhs=False):
        dest_register = "rbx" if is_rhs else "rax"
        self.output.append(f"mov ${literal.literal}, %{dest_register}")

    def compile_identifier(self, identifier, is_rhs=False):
        dest_register = "rbx" if is_rhs else "rax"
        stack_pos = self.stack_positions[identifier.name]
        self.output.append(f"mov {stack_pos}(%rsp), %{dest_register}")

    def compile_binary_operator(self, operator):
        if operator.operator == "+":
            self.output.append("add %rbx, %rax")
        elif operator.operator == "-":
            self.output.append("sub %rbx, %rax")
        elif operator.operator == "*":
            self.output.append("mul %rbx")
        elif operator.operator == "/":
            self.output.append("xor %rdx, %rdx")
            self.output.append("idiv %rbx")
        else:
            assert False, f"Unknown operator {operator.operator}"

    def compile_unary_operation(self, operation, is_rhs=False):
        operand = operation.operand
        if type(operand) is Literal:
            self.compile_literal(operand, is_rhs)
        elif type(operand) is Identifier:
            self.compile_identifier(operand, is_rhs)
        elif type(operand) is UnaryOperation:
            self.compile_unary_operation(operand, is_rhs)
        elif type(operand) is BinaryOperation:
            self.compile_binary_operation(operand, is_rhs)
        else:
            assert False, f"Unknown expression {operation.expr}"
        dest_register = "rbx" if is_rhs else "rax"
        if operation.operator.operator == "-":
            self.output.append(f"neg %{dest_register}")

    def compile_assignment(self, assignment):
        self.compile_expression(assignment.src)
        stack_pos = self.stack_positions[assignment.dst.name]
        self.output.append(f"mov %rax, {stack_pos}(%rsp)")

    def compile_expression(self, expr):
        if type(expr) is Literal:
            self.compile_literal(expr)
        elif type(expr) is Identifier:
            self.compile_identifier(expr)
        elif type(expr) is UnaryOperation:
            self.compile_unary_operation(expr)
        elif type(expr) is BinaryOperation:
            self.compile_binary_operation(expr)

    def compile_decleration(self, decleration):
        self.stack_positions[decleration.identifier.name] = self.stack_top
        self.stack_top += 8
        self.compile_assignment(Assignment(decleration.identifier, decleration.expr))
