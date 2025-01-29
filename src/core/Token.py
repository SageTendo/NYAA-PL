from typing import Union

from src.core.Types import TokenType


class Position:
    """Represents the position of a token in the source code"""

    def __init__(self, *, line: int = -1, col: int = -1) -> None:
        self.line_number = line
        self.column_number = col


class Token:
    """Represents a token"""

    def __init__(self) -> None:
        self._type = TokenType.NULL
        self._word: str = ""
        self._number: Union[int, float] = 0
        self.__position = Position(line=-1, col=-1)

    @property
    def type(self) -> TokenType:
        return self._type

    @type.setter
    def type(self, tok_type: TokenType) -> None:
        self._type = tok_type

    @property
    def value(self):
        return self._type.value

    @property
    def word(self) -> str:
        return self._word

    @word.setter
    def word(self, value: str) -> None:
        self._word = value

    @property
    def number(self) -> Union[int, float]:
        return self._number

    @number.setter
    def number(self, value: Union[int, float]) -> None:
        self._number = value

    @property
    def line_num(self) -> int:
        return self.position.line_number

    @property
    def column_num(self) -> int:
        return self.position.column_number

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position

    def __str__(self) -> str:
        if self._word:
            return f"type: {self._type} -> {self._word}"
        return f"type: {self._type}"
