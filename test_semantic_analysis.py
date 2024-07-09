import pytest

from lexing import Tokenizer
from parsing import Parser
from semantic_analysis import SemanticAnalyzer, UndeclaredError, RedelerationError


def ast_from_code(code: str):
    tokens = Tokenizer().tokenize(code)
    return Parser().parse(tokens)


def test_declaration():
    # This should just pass
    SemanticAnalyzer().analyze(ast_from_code("let foo = 1;"))


def test_undeclared_rhs():
    with pytest.raises(UndeclaredError) as excinfo:
        SemanticAnalyzer().analyze(ast_from_code("let foo = bar;"))
    assert excinfo.value.identifier.name == "bar"


def test_undeclared_lhs():
    with pytest.raises(UndeclaredError) as excinfo:
        SemanticAnalyzer().analyze(ast_from_code("let bar = 1; foo = bar;"))
    assert excinfo.value.identifier.name == "foo"


def test_undeclared_in_return():
    with pytest.raises(UndeclaredError) as excinfo:
        SemanticAnalyzer().analyze(ast_from_code("return bar;"))
    assert excinfo.value.identifier.name == "bar"


def test_redecleration():
    with pytest.raises(RedelerationError) as excinfo:
        SemanticAnalyzer().analyze(ast_from_code("let a = 0;\nlet a = 0;"))
    assert excinfo.value.new_decleration.name == "a"
    assert excinfo.value.first_decleration.pos.line_number == 1
