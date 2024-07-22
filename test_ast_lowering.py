from parsing import Parser
from lexing import Tokenizer
from ast_lowering import LoweringPass
from ir import LoadConstant, LoadVariable, BinaryOperation, UnaryOperation, Return


def ast_from_code(code: str):
    tokens = Tokenizer().tokenize(code)
    ast = Parser().parse(tokens)
    return ast


def ast_from_expr(code: str):
    tokens = Tokenizer().tokenize(code)
    ast = Parser().parse_expression(tokens)
    return [ast]


def test_lowering_literal():
    assert LoweringPass().lower(ast_from_expr("1;")) == [
        LoadConstant("%0", 1),
    ]


def test_lowering_identifier():
    assert LoweringPass().lower(ast_from_expr("a;")) == []


def test_lowering_unary_operation():
    assert LoweringPass().lower(ast_from_expr("-c;")) == [
        UnaryOperation(op="-", var="c"),
    ]


def test_lowering_binary_operation():
    assert LoweringPass().lower(ast_from_expr("b * c;")) == [
        BinaryOperation("%0", "*", "b", "c"),
    ]


def test_lowering_decleration():
    assert LoweringPass().lower(ast_from_code("let a = 1;")) == [
        LoadConstant("%0", 1),
        LoadVariable("a", "%0"),
    ]


def test_lowering_decleration_with_unary_op():
    assert LoweringPass().lower(ast_from_code("let a = -1;")) == [
        LoadConstant("%0", 1),
        UnaryOperation("-", "%0"),
        LoadVariable("a", "%0"),
    ]


def test_lowering_assignment():
    assert LoweringPass().lower(ast_from_code("a = b * c;")) == [
        BinaryOperation("%0", "*", "b", "c"),
        LoadVariable("a", "%0"),
    ]


def test_lowering_return():
    assert LoweringPass().lower(ast_from_code("return c;")) == [
        Return("c"),
    ]
