import pytest

from token_stream import EndOfInputError
from parsing import Parser, UnexpectedTokenError, ExpectedTokenError
from blocks import BinaryOperation, UnaryOperation, Assignment, Return
from tokenization import Tokenizer, Identifier, Literal, Operator, Seperator, Keyword


def test_expression_single_operand():
    tokens = Tokenizer().tokenize("5;")
    assert Parser().parse_expression(tokens) == Literal("5")


def test_expression_simple_operation():
    tokens = Tokenizer().tokenize("5*3;")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        Literal("5"), Operator("*"), Literal("3")
    )


def test_expression_complex():
    tokens = Tokenizer().tokenize("1337 + 420 + 42;")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        BinaryOperation(Literal("1337"), Operator("+"), Literal("420")),
        Operator("+"),
        Literal("42"),
    )


def test_missing_oeprand():
    tokens = Tokenizer().tokenize("5*;")
    with pytest.raises(UnexpectedTokenError):
        Parser().parse_expression(tokens)


def test_parenthesized_experssion():
    tokens = Tokenizer().tokenize("(1+2);")
    expected = BinaryOperation(Literal("1"), Operator("+"), Literal("2"))
    expected.parenthesize()
    assert Parser().parse_expression(tokens) == expected


def test_parenthesized_literal():
    tokens = Tokenizer().tokenize("(5);")
    assert Parser().parse_expression(tokens) == Literal("5")


def test_missing_closing_parenthesis():
    tokens = Tokenizer().tokenize("(5;")
    with pytest.raises(ExpectedTokenError, match='Expected \\) before ";"'):
        Parser().parse_expression(tokens)


def test_simple_assignment():
    tokens = Tokenizer().tokenize("var = 3;")
    assert Parser().parse_assignment(tokens) == Assignment(
        Identifier("var"), Literal("3")
    )


def test_variable_copy():
    tokens = Tokenizer().tokenize("foo = bar;")
    assert Parser().parse_assignment(tokens) == Assignment(
        Identifier("foo"), Identifier("bar")
    )


def test_assigment_of_operation():
    tokens = Tokenizer().tokenize("foo = 1337 - 420;")
    assert Parser().parse_assignment(tokens) == Assignment(
        Identifier("foo"),
        BinaryOperation(Literal("1337"), Operator("-"), Literal("420")),
    )


def test_order_of_operations_left_to_right():
    tokens = Tokenizer().tokenize("1337 + 420 * 42;")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        Literal("1337"),
        Operator("+"),
        BinaryOperation(Literal("420"), Operator("*"), Literal("42")),
    )


def test_order_of_operations_right_to_left():
    tokens = Tokenizer().tokenize("1337 * 420 + 42;")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        BinaryOperation(Literal("1337"), Operator("*"), Literal("420")),
        Operator("+"),
        Literal("42"),
    )


def test_order_of_operation_uneeded_parenthesis():
    tokens = Tokenizer().tokenize("1337 + (420 * 42);")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        Literal("1337"),
        Operator("+"),
        BinaryOperation(Literal("420"), Operator("*"), Literal("42")).parenthesize(),
    )


def test_order_of_operation_needed_parenthesis():
    tokens = Tokenizer().tokenize("(1337 + 420) * 42;")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        BinaryOperation(Literal("1337"), Operator("+"), Literal("420")).parenthesize(),
        Operator("*"),
        Literal("42"),
    )


def test_order_of_operation_double_parenthesis():
    tokens = Tokenizer().tokenize("(1337 + 420) * (42 + 1);")
    assert Parser().parse_expression(tokens) == BinaryOperation(
        BinaryOperation(Literal("1337"), Operator("+"), Literal("420")).parenthesize(),
        Operator("*"),
        BinaryOperation(Literal("42"), Operator("+"), Literal("1")).parenthesize(),
    )


def test_unary_literal():
    tokens = Tokenizer().tokenize("-1")
    assert Parser().parse_operand(tokens) == UnaryOperation(Operator("-"), Literal("1"))


def test_unary_operator_on_expression():
    tokens = Tokenizer().tokenize("-(1 + 2)")
    assert Parser().parse_operand(tokens) == UnaryOperation(
        Operator("-"),
        BinaryOperation(Literal("1"), Operator("+"), Literal("2")).parenthesize(),
    )


def test_unary_operator_on_seperator():
    tokens = Tokenizer().tokenize("-(-(1))")
    assert Parser().parse_operand(tokens) == UnaryOperation(
        Operator("-"), UnaryOperation(Operator("-"), Literal("1"))
    )


def test_return_literal():
    tokens = Tokenizer().tokenize("return -1;")
    assert Parser().parse_keyword(tokens) == Return(
        UnaryOperation(Operator("-"), Literal("1"))
    )


def test_return_variable():
    tokens = Tokenizer().tokenize("return var;")
    assert Parser().parse_keyword(tokens) == Return(Identifier("var"))


def test_return_expression():
    tokens = Tokenizer().tokenize("return var + 1;")
    assert Parser().parse_keyword(tokens) == Return(
        BinaryOperation(Identifier("var"), Operator("+"), Literal("1"))
    )


def test_multiple_statements():
    tokens = Tokenizer().tokenize("var = 2; return var;")
    assert Parser().parse(tokens) == [
        Assignment(Identifier("var"), Literal("2")),
        Return(Identifier("var")),
    ]
