import pytest

from parsing import (
    Parser,
    Operation,
    Assignment,
    EndOfInputError,
    UnexpectedTokenError,
    ExpectedTokenError,
)
from tokenization import Tokenizer, Identifier, Literal, Operator, Seperator, Keyword


def test_simple_operation():
    tokens = Tokenizer().tokenize("5*3")
    assert Parser(tokens).parse_expression() == Operation(
        Literal("5"), Operator("*"), Literal("3")
    )


def test_missing_oeprand():
    tokens = Tokenizer().tokenize("5*;")
    with pytest.raises(UnexpectedTokenError):
        Parser(tokens).parse_expression()


def test_missing_end_of_input():
    tokens = Tokenizer().tokenize("5*")
    with pytest.raises(EndOfInputError):
        Parser(tokens).parse_expression()


def test_parenthesized_experssion():
    tokens = Tokenizer().tokenize("(1+2);")
    expected = Operation(Literal("1"), Operator("+"), Literal("2"))
    expected.parenthesize()
    assert Parser(tokens).parse_expression() == expected


def test_parenthesized_literal():
    tokens = Tokenizer().tokenize("(5);")
    assert Parser(tokens).parse_expression() == Literal("5")


def test_missing_closing_parenthesis():
    tokens = Tokenizer().tokenize("(5;")
    with pytest.raises(ExpectedTokenError):
        Parser(tokens).parse_expression()


def test_simple_assignment():
    tokens = Tokenizer().tokenize("var = 3;")
    assert Parser(tokens).parse_assignment() == Assignment(
        Identifier("var"), Literal("3")
    )


def test_variable_copy():
    tokens = Tokenizer().tokenize("foo = bar;")
    assert Parser(tokens).parse_assignment() == Assignment(
        Identifier("foo"), Identifier("bar")
    )


def test_assigment_of_operation():
    tokens = Tokenizer().tokenize("foo = 1337 - 420;")
    assert Parser(tokens).parse_assignment() == Assignment(
        Identifier("foo"),
        Operation(Literal("1337"), Operator("-"), Literal("420")),
    )
