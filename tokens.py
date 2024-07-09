from position import Position


class Token:
    def __init__(self, raw: str, pos: Position):
        self.pos = pos
        self.raw = raw

    def __repr__(self):
        return f"{type(self).__name__}({self.raw})"


class Identifier(Token):
    def __init__(self, name: str, pos: Position = None):
        super().__init__(name, pos)
        self.name = name

    def __eq__(self, other):
        return self.name == other.name


class Keyword(Token):
    KEYWORDS = {"return", "let"}

    def __init__(self, keyword: str, pos: Position = None):
        super().__init__(keyword, pos)
        if keyword not in self.KEYWORDS:
            raise ValueError()
        self.keyword = keyword

    def __eq__(self, other):
        return self.keyword == other.keyword


class Seperator(Token):
    SEPERATORS = set("();")

    def __init__(self, seperator: str, pos: Position = None):
        super().__init__(seperator, pos)
        if seperator not in self.SEPERATORS:
            raise ValueError()
        self.seperator = seperator

    def __eq__(self, other):
        return self.seperator == other.seperator


class Literal(Token):
    def __init__(self, literal: str, pos: Position = None):
        super().__init__(literal, pos)
        self.literal = int(literal)

    def __eq__(self, other):
        return self.literal == other.literal


class Operator(Token):
    OPERATORS = set("+-*/=")

    def __init__(self, operator: str, pos: Position = None):
        super().__init__(operator, pos)
        if operator not in self.OPERATORS:
            raise ValueError()
        self.operator = operator

    def __eq__(self, other):
        return self.operator == other.operator
