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
        self.output.extend(self.PROLOGUE)
        while self.index < len(self.blocks):
            block = self.blocks[self.index]
            self.index += 1
            if type(block) is Return:
                self.compile_return(block)
            elif type(block) is Assignment:
                assert False, "TODO"
            else:
                assert False, f"Unknown expression {block}"
        self.output.extend(self.EPILOGUE)
        return self.output

    def compile_return(self, statement):
        if type(statement.expr) is Literal:
            self.compile_literal(statement.expr)
        elif type(statement.expr) is Identifier:
            assert False, "TODO"
        elif type(statement.expr) is Expression:
            assert False, "TODO"
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

    def compile_literal(self, literal, is_rhs=False):
        dest_register = "rbx" if is_rhs else "rax"
        self.output.append(f"mov ${literal.literal}, %{dest_register}")

