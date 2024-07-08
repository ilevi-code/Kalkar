from position import Position
from tokens import Token


class CompilationError(Exception):
    def __init__(self, position: Position, highlight_len: int, message: str):
        self.position = position
        self.highlight_len = highlight_len
        self.message = message
        self.secondary_message = None

    def with_secondary_message_at_token(self, token: Token, message: str):
        self.secondary_message = (
            CompilationError.highlight(token.pos, len(token.raw), message, "-") + "\n"
        )
        return self

    def __str__(self):
        message = self.secondary_message or ""
        return message + CompilationError.highlight(
            self.position, self.highlight_len, self.message, "^"
        )

    @staticmethod
    def highlight(
        position: Position, highlight_len: int, message: str, char_under: str
    ):
        space_pad = " " * position.offset
        highlight = "^" * highlight_len
        line_number_fill = " " * len(str(position.line_number))
        return "\n".join(
            [
                f"{position.line_number} | {position.line}",
                f"{line_number_fill} | {space_pad}{highlight} {message}",
            ]
        )
