class Compiler:
    PROLOGUE = """
.global main
main:
push %rbp
mov  %rsp, %rbp
"""
    EPILOGUE = """
mov %rax, %rsi
lea  format(%rip), %rdi
call printf

mov %rbp, %rsp
pop %rbp
ret

format:
.asciz "%d\\n"
"""
    def __init__(self, output):
        self.output = output
        self.stack_positions = {}
        self.stack_top = 0

    def compile(self, blocks):
        self.output.write(self.PROLOGUE)
        self.output.write(self.EPILOGUE)
