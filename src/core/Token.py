from typing import Tuple, Union

from src.core.Types import TokenType


class Token:
    """Represents a token"""

    def __init__(self) -> None:
        self._type = TokenType.NULL
        self._word: str = ""
        self._number: Union[int, float] = 0
        self.pos: Tuple[int, int] = (-1, -1)

    @property
    def type(self) -> TokenType:
        return self._type

    @type.setter
    def type(self, tok_type: TokenType) -> None:
        self._type = tok_type

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
        return self.pos[0]

    @property
    def column_num(self) -> int:
        return self.pos[1]

    def __str__(self) -> str:
        if self._word:
            return f"type: {self._type} -> {self._word}"
        return f"type: {self._type}"
