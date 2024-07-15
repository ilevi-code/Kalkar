from typing import Dict
from functools import singledispatchmethod
from itertools import cycle

from ir import LoadConstant, LoadVariable, BinaryOperation, UnaryOperation, Return


class Variable:
    def __init__(self):
        self.stack_pos = None
        self.reg = None


class CodeGen:
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
        self.variables: Dict[str, Variable] = {}
        self.regs: Dict[str, Variable] = {}
        self.reg_cycle = iter(cycle(["rax", "rbx"]))
        self.stack_top = 0

    def code_gen(self, ir):
        for instruction in ir:
            self.compile_instruction(instruction)
        self.align_stack()
        total = self.PROLOGUE.copy()
        if self.stack_top != 0:
            total.append(f"sub ${self.stack_top}, %rsp")
        total.extend(self.output)
        total.extend(self.EPILOGUE)
        return total

    @singledispatchmethod
    def compile_instruction(self, instrcution):
        raise TypeError(f"Unknown instruction: {instrcution}")

    @compile_instruction.register
    def compile_load_const(self, load: LoadConstant):
        reg = self.get_reg()
        self.output.append(f"mov ${load.value}, %{reg}")
        var = self.get_var(load.dest)
        self.regs[reg] = var
        var.reg = reg

    @compile_instruction.register
    def compile_load_var(self, load: LoadVariable):
        source = self.get_var(load.source)
        reg = self.get_reg()
        if source.reg is not None:
            self.output.append(f"mov %{source.reg}, %{reg}")
        else:
            self.output.append(f"mov {source.stack_pos}(%rsp), %{reg}")
        dest = self.get_var(load.dest)
        self.regs[reg] = dest
        dest.reg = reg

    def get_var(self, var_name: str) -> Variable:
        return self.variables.setdefault(var_name, Variable())

    def get_reg(self, exclude_reg=None) -> str:
        while (reg := next(self.reg_cycle)) == exclude_reg:
            pass
        self.assure_register_is_free(reg)
        return reg

    def assure_register_is_free(self, reg):
        """Stores the variable who's using the register"""
        try:
            var = self.regs[reg]
        except KeyError:
            return
        self.store(var)
        self.free_reg(var.reg)

    def store(self, var: Variable):
        if var.stack_pos is None:
            var.stack_pos = self.alloc_stack()
        self.output.append(f"mov %{var.reg}, {var.stack_pos}(%rsp)")

    def alloc_stack(self):
        pos = self.stack_top
        self.stack_top += 8
        return pos

    def free_reg(self, reg: str):
        if reg not in self.regs:
            return
        self.regs[reg].reg = None
        self.regs.pop(reg)

    @compile_instruction.register
    def compile_unary_op(self, operation: UnaryOperation):
        assert operation.op == "-"
        var = self.load_backup(operation.var)
        self.output.append(f"neg %{var.reg}")

    def load_backup(self, var_name, exclude_reg=None):
        var = self.get_var(var_name)
        if var.reg is None:
            self.load(var_name, exclude_reg)
        else:
            self.store(var)
        return var

    def load(self, var_name: str, exclude_reg=None) -> Variable:
        var = self.get_var(var_name)
        if var.reg is None:
            reg = self.get_reg(exclude_reg)
            self.output.append(f"mov {var.stack_pos}(%rsp), %{reg}")
            self.regs[reg] = var
            var.reg = reg
        return var

    @compile_instruction.register
    def compile_binary_op(self, operation: BinaryOperation):
        operation_compiler = {
            "+": self.compile_add,
            "-": self.compile_sub,
            "*": self.compile_mul,
            "/": self.compile_div,
        }[operation.op]
        lhs = self.load_backup(operation.lhs)
        rhs = self.load(operation.rhs, exclude_reg=lhs.reg)
        output_reg = operation_compiler(lhs, rhs)
        output_var = self.get_var(operation.dest)
        output_var.reg = output_reg
        self.regs[output_reg] = output_var

    def compile_add(self, lhs: Variable, rhs: Variable):
        self.output.append(f"add %{rhs.reg}, %{lhs.reg}")
        return lhs.reg

    def compile_sub(self, lhs: Variable, rhs: Variable):
        self.output.append(f"sub %{rhs.reg}, %{lhs.reg}")
        return lhs.reg

    def compile_mul(self, lhs: Variable, rhs: Variable):
        self.assure_variable_in_reg(lhs, "rax")
        self.output.append(f"mul %{rhs.reg}")
        return "rax"

    def assure_variable_in_reg(self, var: Variable, reg: str):
        if var.reg == reg:
            return
        try:
            switched = self.regs[reg]
            self.output.append(f"xchg %{var.reg}, %{reg}")
            switched.reg = var.reg
            self.regs[var.reg] = switched
        except KeyError:
            self.output.append(f"mov %{var.reg}, %{reg}")
        var.reg = reg
        self.regs[reg] = var

    def compile_div(self, lhs: Variable, rhs: Variable):
        self.assure_variable_in_reg(lhs, "rax")
        self.output.extend(
            [
                "cqo",
                f"idiv %{rhs.reg}",
            ]
        )
        return "rax"

    @compile_instruction.register
    def compile_return(self, ret: Return):
        var = self.load(ret.var)
        self.output.extend(
            [
                f"mov %{var.reg}, %rsi",
                "lea  format(%rip), %rdi",
                "call printf",
                "mov %rbp, %rsp",
                "pop %rbp",
                "mov $0, %rax",
                "ret",
            ]
        )

    def align_stack(self):
        self.stack_top = (self.stack_top + (self.STACK_ALIGNMENT - 1)) & ~(
            self.STACK_ALIGNMENT - 1
        )
