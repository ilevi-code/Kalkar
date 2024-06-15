from blocks import Expression, Assignment, Return
from tokens import Identifier, Literal


class Compiler:
    PROLOGUE = [
'.global main',
"main:",
"push %rbp",
"mov  %rsp, %rbp",
]
    EPILOGUE = [
".section .rodata",
"format:",
'.asciz "%d\\n"',
]

    def __init__(self, blocks):
        self.output = []
        self.blocks = blocks
        self.stack_positions = {}
        self.stack_top = 0
        self.index = 0

    def compile(self):
        while self.index < len(self.blocks):
            block = self.blocks[self.index]
            self.index += 1
            if type(block) is Return:
                self.compile_return(block)
            elif type(block) is Assignment:
                self.compile_assignment(block)
            else:
                assert False, f"Unknown expression {block}"
        total = self.PROLOGUE.copy()
        total.append(f"sub ${self.stack_top}, %rsp")
        total.extend(self.output)
        total.extend(self.EPILOGUE)
        return total

    def compile_return(self, statement):
        if type(statement.expr) is Literal:
            self.compile_literal(statement.expr)
        elif type(statement.expr) is Identifier:
            self.compile_identifier(statement.expr)
        elif type(statement.expr) is Expression:
            self.compile_expression(statement.expr)
        else:
            assert False, f"Unknown expression {statement.expr}"
        self.output.extend(
            [
                "mov %rax, %rsi",
                "lea  format(%rip), %rdi",
                "call printf",
                "mov %rbp, %rsp",
                "pop %rbp",
                "ret",
            ]
        )

    def compile_expression(self, expr):
        for operand, is_rhs in [(expr.lhs, False), (expr.rhs, True)]:
            if type(operand) is Literal:
                self.compile_literal(operand, is_rhs)
            elif type(operand) is Identifier:
                self.compile_identifier(operand, is_rhs)
            elif type(operand) is Expression:
                if is_rhs:
                    self.output.append("push %rax")
                self.compile_expression(operand)
                if is_rhs:
                    self.output.append("mov %rax, %rbx")
                    self.output.append("pop %rax")
            else:
                assert False, f"Unknown expression {statement.expr}"
        self.compile_operator(expr.operator)

    def compile_literal(self, literal, is_rhs=False):
        dest_register = "rbx" if is_rhs else "rax"
        self.output.append(f"mov ${literal.literal}, %{dest_register}")

    def compile_identifier(self, identifier, is_rhs=False):
        dest_register = "rbx" if is_rhs else "rax"
        stack_pos = self.stack_positions[identifier.name]
        self.output.append(f"mov {stack_pos}(%rsp), %{dest_register}")

    def compile_operator(self, operator):
        if operator.operator == '+':
            self.output.append("add %rbx, %rax")
        elif operator.operator == '-':
            self.output.append("sub %rbx, %rax")
        elif operator.operator == '*':
            self.output.append("mul %rbx")
        elif operator.operator == '/':
            self.output.append("xor %rdx, %rdx")
            self.output.append("idiv %rbx")
        else:
            assert False, f"Unknown operator {operator.operator}"

    def compile_assignment(self, assignment):
        if assignment.dst.name not in self.stack_positions:
            self.stack_positions[assignment.dst.name] = self.stack_top
            self.stack_top += 8
        src = assignment.src
        if type(src) is Literal:
            self.compile_literal(src)
        elif type(src) is Identifier:
            self.compile_identifier(src)
        elif type(src) is Expression:
            self.compile_expression(src)
        stack_pos = self.stack_positions[assignment.dst.name]
        self.output.append(f"mov %rax, {stack_pos}(%rsp)")
