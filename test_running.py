import subprocess
import tempfile
import contextlib
import os

import pytest

from lexing import Tokenizer
from parsing import Parser
from compilation import Compiler


@contextlib.contextmanager
def temp_path():
    try:
        yield "./a.out"
    finally:
        os.unlink("./a.out")


def compile_and_run(code: str):
    tokens = Tokenizer().tokenize(code)
    ast = Parser().parse(tokens)
    instructions = Compiler().compile(ast)
    with tempfile.NamedTemporaryFile(mode="w") as output, temp_path() as binary_path:
        output.write("\n".join(instructions))
        output.flush()
        subprocess.run(
            ["gcc", "-x", "assembler", output.name, "-o", binary_path], check=True
        )
        child = subprocess.run([binary_path], capture_output=True, check=True)
    return int(child.stdout)


def test_return_literal():
    assert compile_and_run("return 1;") == 1


def test_nagtive_literal():
    assert compile_and_run("return -1;") == -1


def test_multiplication():
    assert compile_and_run("return 2 * 3;") == 6


def test_divistion():
    assert compile_and_run("return 20 / 3;") == 6


def test_return_variable():
    assert compile_and_run("a = 2; return a;") == 2


def test_multiple_variable():
    assert compile_and_run("a=1;b=2;c=3;d=4;e=5;return a+b+c+d+e;") == 15


@pytest.mark.parametrize(
    "code",
    [
        "return -3;",
        "a = 3; return -a;",
        "a = -2; return a + -1;",
        "return -(2 + 1);",
        "return -(-(2 - 5));",
    ],
)
def test_unary_operations(code):
    assert compile_and_run(code) == -3


@pytest.mark.parametrize(
    "code,expected",
    [
        ("return 2 + 3 * 5;", 17),
        ("return 2 * 3 + 5;", 11),
        ("return 2 * (3 + 5);", 16),
    ],
)
def test_order_of_operations(code, expected):
    assert compile_and_run(code) == expected


def test_adding_negative_literal():
    assert compile_and_run("a = 7 + -3; return a * 5;") == 20


def test_adding_return_variable():
    assert compile_and_run("a2 = 4; return a2;") == 4
