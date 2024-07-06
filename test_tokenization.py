import pytest

from position import Position
from lexing import Tokenizer, UnknownCharacher, LineScanner


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
    assert Tokenizer().tokenize("var_name").pop().name == "var_name"


def test_single_keyword():
    assert Tokenizer().tokenize("return").pop().keyword == "return"


def test_single_operator():
    assert Tokenizer().tokenize("+").pop().operator == "+"


def test_single_seperator():
    assert Tokenizer().tokenize("(").pop().seperator == "("


def test_single_literal():
    assert Tokenizer().tokenize("1337").pop().literal == 1337


def test_first_position():
    assert Tokenizer().tokenize("1337").pop().pos == Position("1337", 1, 0)


def test_second_position():
    tokens = Tokenizer().tokenize("var =")
    tokens.pop()
    assert tokens.pop().pos == Position("var =", 1, 4)


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
