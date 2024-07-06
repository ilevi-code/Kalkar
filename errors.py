from position import Position


class CompilationError(Exception):
    def __init__(self, position: Position, highlight_len: int, message: str):
        self.position = position
        self.highlight_len = highlight_len
        self.message = message

    def __str__(self):
        space_pad = " " * self.position.offset
        highlight = "^" * self.highlight_len
        return f"{self.position.line_number}: {self.message}\n{self.position.line}\n{space_pad}{highlight}"
