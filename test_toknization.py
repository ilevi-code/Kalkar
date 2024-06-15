import pytest

from position import Position
from tokens import Identifier, Keyword, Seperator, Literal, Operator
from tokenization import Tokenizer, UnknownCharacher, LineScanner


@pytest.mark.parametrize(
    "word",
    [
        ("var_name"),
        ("1337"),
        ("="),
        ("("),
        (")"),
        ("return"),
    ],
)
def test_single_word(word):
    assert LineScanner(word, 0).read() == word


@pytest.mark.parametrize(
    "line,expected",
    [
        ("func()", ["func", "(", ")"]),
        ("a = (b + 15)", ["a", "=", "(", "b", "+", "15", ")"]),
    ],
)
def test_splitting(line, expected):
    words = []
    line_scanner = LineScanner(line, 0)
    while word := line_scanner.read():
        words.append(word)
    assert words == expected


def test_space_skipping():
    words = []
    line_scanner = LineScanner("    a  = 1   ", 0)
    while word := line_scanner.read():
        words.append(word)
    assert words == ["a", "=", "1"]


def test_single_identifier():
    assert Tokenizer().tokenize("var_name")[0].name == "var_name"


def test_single_keyword():
    assert Tokenizer().tokenize("return")[0].keyword == "return"


def test_single_operator():
    assert Tokenizer().tokenize("+")[0].operator == "+"


def test_single_seperator():
    assert Tokenizer().tokenize("(")[0].seperator == "("


def test_single_literal():
    assert Tokenizer().tokenize("1337")[0].literal == 1337

def test_negative_literal():
    assert Tokenizer().tokenize("-42")[0].literal == -42

def test_first_position():
    assert Tokenizer().tokenize("1337")[0].pos == Position("1337", 1, 0)

def test_second_position():
    assert Tokenizer().tokenize("var =")[1].pos == Position("var =", 1, 4)

def test_error_position():
    try:
        Tokenizer().tokenize("1337\na = 1$")
    except UnknownCharacher as e:
        assert e.position == Position("a = 1$", 2, 5)
    else:
        assert False, "Didn't raise"

def test_unkown_char():
    with pytest.raises(UnknownCharacher):
        Tokenizer().tokenize("$")
