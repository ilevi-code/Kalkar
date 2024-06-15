import subprocess
import tempfile
import pytest

from compilation import Compiler
from parsing import Parser
from tokenization import Tokenizer


def compile_and_run(code: str):
    tokens = Tokenizer().tokenize(code)
    ast = Parser(tokens).parse()
    instructions = Compiler(ast).compile()
    with tempfile.NamedTemporaryFile(mode="w") as output:
        output.write("\n".join(instructions))
        output.flush()
        subprocess.run(
            ["gcc", "-x", "assembler", output.name, "-o", "a.out"], check=True
        )
    child = subprocess.run(["./a.out"], capture_output=True, check=True)
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
    assert (
        compile_and_run("a=1;b=2;c=3;d=4;e=5;return a+b+c+d+e;")
        == 15
    )

@pytest.mark.parametrize('code,expected', [
    ("return 2 + 3 * 5;", 17),
    ("return 2 * 3 + 5;", 11),
    ("return 2 * (3 + 5);", 16),
    ])
def test_order_of_operations(code, expected):
    assert compile_and_run(code) == expected

def test_adding_negative_literal():
    assert compile_and_run("a = 7 + -3; return a * 5;") == 20

def test_adding_negative_literal():
    assert compile_and_run("a2 = 4; return a2;") == 4
