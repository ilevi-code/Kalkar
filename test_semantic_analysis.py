import pytest

from lexing import Tokenizer
from parsing import Parser
from semantic_analysis import SemanticAnalyzer, SemanticError


def ast_from_code(code: str):
    tokens = Tokenizer().tokenize(code)
    return Parser().parse(tokens)


def test_declaration():
    # This should just pass
    SemanticAnalyzer().analyze(ast_from_code("foo = 1;"))


@pytest.mark.parametrize(
    "blocks",
    [
        ast_from_code("foo = bar;"),
        ast_from_code("bar = 1; foo = bar * 2;"),
        ast_from_code("bar = 1; foo = 1 + (2 * bar);"),
        ast_from_code("return bar;"),
    ],
)
def test_undeclared(blocks):
    with pytest.raises(SemanticError, match="bar"):
        SemanticAnalyzer().analyze(blocks)
