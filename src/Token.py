from enum import Enum, auto


class TokenType(Enum):
    """Token types."""
    TOK_COMMENT = auto()  # Comment
    TOK_ID = auto()  # Identifier
    TOK_INT = auto()  # Integer
    TOK_STR = auto()  # String
    TOK_EOF = auto()  # End of file

    # Keywords
    TOK_NYAA_FUNC = auto()  # Function
    TOK_MAIN_NYAA = auto()  # Main
    TOK_SAY = auto()  # Print
    TOK_LISTEN = auto()  # input
    TOK_GIVE_BACK = auto()  # return

    TOK_WHILE = auto()  # while
    TOK_IF = auto()  # if
    TOK_ELSE = auto()  # else
    TOK_ELIF = auto()  # elif

    # Operators
    TOK_PLUS = auto()  # +
    TOK_MINUS = auto()  # -
    TOK_MULTIPLY = auto()  # *
    TOK_DIVIDE = auto()  # /
    TOK_MODULO = auto()  # %

    # Boolean operators
    TOK_AND = auto()  # &&
    TOK_OR = auto()  # ||
    TOK_EQ = auto()  # ==
    TOK_NOT = auto()  # not
    TOK_NEQ = auto()  # !=
    TOK_LT = auto()  # <
    TOK_GT = auto()  # >
    TOK_LTE = auto()  # <=
    TOK_GTE = auto()  # >=
    TOK_IS = auto()  # is

    # Non-alphabetic operators
    TOK_ASSIGN = auto()  # =
    TOK_LPAR = auto()  # (
    TOK_RPAR = auto()  # )
    TOK_COMMA = auto()  # ,
    TOK_TYPE_ASSIGN = auto()  # ::
    TOK_SEMICOLON = auto()  # ;
    TOK_LBRACKET = auto()  # [
    TOK_RBRACKET = auto()  # ]
    TOK_LBRACE = auto()  # {
    TOK_RBRACE = auto()  # }

    def __str__(self):
        return self.name


class Token:
    def __init__(self):
        self._type = None
        self._value = None
        self._word = None
        self._string = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, tok_type):
        self._type = tok_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def word(self):
        return self._word

    @word.setter
    def word(self, word):
        self._word = word

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, string):
        self._string = string

    def __str__(self):
        val = None
        if self._value is not None:
            val = self._value
        elif self._word is not None:
            val = self._word
        elif self._string is not None:
            val = self._string

        if val is not None:
            return f"type={self._type} -> {val}"
        return f"type={self._type}"
