import pytest

from parsing import Parser, EndOfInputError, UnexpectedTokenError, ExpectedTokenError
from blocks import Expression, Assignment, Return

from tokenization import Tokenizer, Identifier, Literal, Operator, Seperator, Keyword


def test_expression_single_operand():
    tokens = Tokenizer().tokenize("5;")
    assert Parser(tokens).parse_expression() == Literal("5")


def test_expression_simple_operation():
    tokens = Tokenizer().tokenize("5*3;")
    assert Parser(tokens).parse_expression() == Expression(
        Literal("5"), Operator("*"), Literal("3")
    )


def test_expression_complex():
    tokens = Tokenizer().tokenize("1337 + 420 + 42;")
    assert Parser(tokens).parse_expression() == Expression(
        Expression(Literal("1337"), Operator("+"), Literal("420")),
        Operator("+"),
        Literal("42"),
    )


def test_missing_oeprand():
    tokens = Tokenizer().tokenize("5*;")
    with pytest.raises(UnexpectedTokenError):
        Parser(tokens).parse_expression()


def test_parenthesized_experssion():
    tokens = Tokenizer().tokenize("(1+2);")
    expected = Expression(Literal("1"), Operator("+"), Literal("2"))
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
        Expression(Literal("1337"), Operator("-"), Literal("420")),
    )


def test_order_of_operations_left_to_right():
    tokens = Tokenizer().tokenize("1337 + 420 * 42;")
    assert Parser(tokens).parse_expression() == Expression(
        Literal("1337"),
        Operator("+"),
        Expression(Literal("420"), Operator("*"), Literal("42")),
    )


def test_order_of_operations_right_to_left():
    tokens = Tokenizer().tokenize("1337 * 420 + 42;")
    assert Parser(tokens).parse_expression() == Expression(
        Expression(Literal("1337"), Operator("*"), Literal("420")),
        Operator("+"),
        Literal("42"),
    )


def test_order_of_operation_uneeded_parenthesis():
    tokens = Tokenizer().tokenize("1337 + (420 * 42);")
    assert Parser(tokens).parse_expression() == Expression(
        Literal("1337"),
        Operator("+"),
        Expression(Literal("420"), Operator("*"), Literal("42")).parenthesize(),
    )


def test_order_of_operation_needed_parenthesis():
    tokens = Tokenizer().tokenize("(1337 + 420) * 42;")
    assert Parser(tokens).parse_expression() == Expression(
        Expression(Literal("1337"), Operator("+"), Literal("420")).parenthesize(),
        Operator("*"),
        Literal("42"),
    )


def test_order_of_operation_double_parenthesis():
    tokens = Tokenizer().tokenize("(1337 + 420) * (42 + 1);")
    assert Parser(tokens).parse_expression() == Expression(
        Expression(Literal("1337"), Operator("+"), Literal("420")).parenthesize(),
        Operator("*"),
        Expression(Literal("42"), Operator("+"), Literal("1")).parenthesize(),
    )


def test_return_literal():
    tokens = Tokenizer().tokenize("return -1;")
    assert Parser(tokens).parse_keyword() == Return(Literal("-1"))


def test_return_variable():
    tokens = Tokenizer().tokenize("return var;")
    assert Parser(tokens).parse_keyword() == Return(Identifier("var"))


def test_return_expression():
    tokens = Tokenizer().tokenize("return var + 1;")
    assert Parser(tokens).parse_keyword() == Return(
        Expression(Identifier("var"), Operator("+"), Literal("1"))
    )


def test_multiple_statements():
    tokens = Tokenizer().tokenize("var = 2; return var;")
    assert Parser(tokens).parse() == [
        Assignment(Identifier("var"), Literal("2")),
        Return(Identifier("var")),
    ]
