import pytest

from position import Position, Line
from tokens import (
    Identifier,
    Keyword,
    Seperator,
    Literal,
    Operator,
    TokenKind,
)
from lexing import Tokenizer, UnknownCharacher


def tokenize_once(line: str) -> TokenKind:
    tokens = Tokenizer.tokenize_line(Line(line, 0))
    assert len(tokens) == 1
    return tokens[0]


def test_tokenization_identifier():
    assert tokenize_once("var_name") == Identifier("var_name")


def test_tokenization_keyword():
    assert tokenize_once("return") == Keyword("return")


def test_tokenization_operator():
    assert tokenize_once("+") == Operator("+")


def test_tokenization_seperator():
    assert tokenize_once("(") == Seperator("(")


def test_tokenization_literal():
    assert tokenize_once("1337") == Literal("1337")


def test_whitespace_are_ignored():
    assert Tokenizer.tokenize_line(Line("   ", 0)) == []


def test_tokenize_assignment():
    assert Tokenizer.tokenize_line(Line("(b + 15)", 0)) == [
        Seperator("("),
        Identifier("b"),
        Operator("+"),
        Literal("15"),
        Seperator(")"),
    ]


def test_first_position():
    assert Tokenizer.tokenize_line(Line("1337", 1))[0].pos == Position(
        Line("1337", 1), 0, 4
    )


def test_second_position():
    assert Tokenizer.tokenize_line(Line("var=", 1))[1].pos == Position(
        Line("var=", 1), 3, 4
    )


def test_unkown_char():
    with pytest.raises(UnknownCharacher):
        Tokenizer().tokenize("$")


def test_error_position():
    with pytest.raises(UnknownCharacher) as excinfo:
        Tokenizer().tokenize("1337\na = 1$")
    assert excinfo.value.position == Position(Line("a = 1$", 2), 5, 6)
