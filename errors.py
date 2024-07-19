from position import Position
from tokens import Token


class CompilationError(Exception):
    def __init__(self, position: Position, message: str):
        self.position = position
        self.message = message
        self.secondary_message = None

    def with_secondary_message_at_token(self, token: Token, message: str):
        self.secondary_message = (
            CompilationError.highlight(token.pos, message, "-") + "\n"
        )
        return self

    def __str__(self):
        message = self.secondary_message or ""
        return message + CompilationError.highlight(self.position, self.message, "^")

    @staticmethod
    def highlight(position: Position, message: str, char_under: str):
        space_pad = " " * position.start
        highlight = "^" * (position.end - position.start)
        line_number_fill = " " * len(str(position.line.number))
        return "\n".join(
            [
                f"{position.line.number} | {position.line.content}",
                f"{line_number_fill} | {space_pad}{highlight} {message}",
            ]
        )
