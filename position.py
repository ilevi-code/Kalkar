class Position:
    def __init__(self, line: str, line_number: int, offset: int):
        self.line = line
        self.line_number = line_number
        self.offset = offset

    def __eq__(self, other):
        return self.line == other.line and self.line_number == other.line_number and self.offset == other.offset
