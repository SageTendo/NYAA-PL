from typing import Optional, Tuple, Union
from src.core.Types import TokenType


class Token:
    """Represents a token"""

    def __init__(self):
        self._type = TokenType.NULL
        self._value: Optional[Union[int, float, str]] = None
        self.pos: Tuple[int, int] = (-1, -1)

    @property
    def type(self) -> TokenType:
        return self._type

    @type.setter
    def type(self, tok_type: TokenType):
        self._type = tok_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def line_num(self) -> int:
        return self.pos[0]

    @property
    def column_num(self) -> int:
        return self.pos[1]

    def __str__(self):
        if self.value:
            return f"type: {self._type} -> {self.value}"
        return f"type: {self._type}"
