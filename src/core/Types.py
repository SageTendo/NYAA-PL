from enum import Enum, auto

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.Token import Token


class TokenType(Enum):
    """Token types"""

    NULL = auto()  # null token

    # Program start
    MAIN = auto()  # uWu_nyaa

    # Types
    INT = auto()  # inteja
    STR = auto()  # soturingu
    FLOAT = auto()  # furoto
    BOOL = auto()  # buru

    # Statements (Independent)
    ID = auto()  # Identifier
    DEF = auto()  # kawaii
    IF = auto()  # if
    WHILE = auto()  # while
    FOR = auto()
    INPUT = auto()  # ohayo
    PRINT = auto()  # yomu
    PRINTLN = auto()  # yomu_ln
    TRUE = auto()  # HAI
    FALSE = auto()  # IIE

    # File access
    FILE_OPEN = auto()  # akeru
    FILE_CLOSE = auto()  # tojiru
    FILE_READ = auto()  # moji
    FILE_READLINE = auto()  #
    FILE_WRITE = auto()  #
    FILE_WRITELINE = auto()  #
    FILE_EOF = auto()  #

    # Breaks
    CONTINUE = auto()  # motto
    BREAK = auto()  # yamete
    RET = auto()  # modoru

    # Dependent statements
    ELIF = auto()  # elif
    ELSE = auto()  # else
    ASSIGN = auto()  # wa

    # Non-alphabetic operators
    TO = auto()  # =>
    LPAR = auto()  # (
    RPAR = auto()  # )
    SEMICOLON = auto()  # ;
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,
    # PERIOD = auto()  # .
    DCOLON = auto()  # ::

    # Binary operators
    PLUS = auto()  # purasu
    MINUS = auto()  # mainasu
    MULTIPLY = auto()  # purodakuto
    DIVIDE = auto()  # supuritto
    MODULO = auto()  # %
    EQ = auto()  # ==
    NEQ = auto()  # !=
    LT = auto()  # <
    GT = auto()  # >
    LTE = auto()  # <=
    GTE = auto()  # >=
    AND = auto()  # ando
    OR = auto()  # matawa

    # Unary operators
    NOT = auto()  # nai
    NEG = auto()  # -
    UN_ADD = auto()  # ++
    UN_SUB = auto()  # --

    ENDMARKER = auto()  # End of file
    ERR = auto()  # Lexer only

    @classmethod
    def statement_start(cls, token: "Token") -> bool:
        return token.type in [
            TokenType.RET,
            TokenType.ID,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.IF,
            TokenType.PRINT,
            TokenType.INPUT,
            TokenType.PRINTLN,
        ]

    @classmethod
    def conditional_stmt_start(cls, token: "Token") -> bool:
        return cls.statement_start(token) or token.type in [
            TokenType.BREAK,
            TokenType.CONTINUE,
        ]

    @classmethod
    def postfix(cls, token: "Token") -> bool:
        return token.type in [TokenType.UN_ADD, TokenType.UN_SUB]

    @classmethod
    def unary(cls, token) -> bool:
        return token.type in [TokenType.NEG, TokenType.NOT]

    @classmethod
    def expression(cls, token: "Token") -> bool:
        return cls.factor(token)

    @classmethod
    def term(cls, token: "Token") -> bool:
        return cls.factor(token)

    @classmethod
    def factor(cls, token: "Token") -> bool:
        return token.type in [
            TokenType.ID,
            TokenType.INT,
            TokenType.STR,
            TokenType.FLOAT,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.LPAR,
            TokenType.NEG,
            TokenType.NOT,
        ]

    @classmethod
    def bin_op(cls, token: "Token") -> bool:
        return cls.rel_op(token) or cls.add_op(token) or cls.mul_op(token)

    @classmethod
    def rel_op(cls, token: "Token") -> bool:
        return token.type in [
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LTE,
            TokenType.GTE,
        ]

    @classmethod
    def add_op(cls, token: "Token") -> bool:
        return token.type in [TokenType.PLUS, TokenType.MINUS, TokenType.OR]

    @classmethod
    def mul_op(cls, token: "Token") -> bool:
        return token.type in [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.AND]

    @classmethod
    def callable(cls, token: "Token") -> bool:
        return token.type in [
            TokenType.ID,
            TokenType.PRINT,
            TokenType.INPUT,
            TokenType.PRINTLN,
        ]

    @classmethod
    def assignment(cls, token: "Token") -> bool:
        return token.type in [TokenType.ASSIGN, TokenType.LBRACKET]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


RESERVED_WORDS = {
    "uWu_nyaa": TokenType.MAIN,
    "yomu": TokenType.PRINT,
    "ohayo": TokenType.INPUT,
    "daijoubu": TokenType.WHILE,
    "nani": TokenType.IF,
    "nandesuka": TokenType.ELIF,
    "baka": TokenType.ELSE,
    "yamete": TokenType.BREAK,
    "motto": TokenType.CONTINUE,
    "kawaii": TokenType.DEF,
    "HAI": TokenType.TRUE,
    "IIE": TokenType.FALSE,
    "wa": TokenType.ASSIGN,
    "modoru": TokenType.RET,
    "purasu": TokenType.PLUS,
    "mainasu": TokenType.MINUS,
    "purodakuto": TokenType.MULTIPLY,
    "supuritto": TokenType.DIVIDE,
    "ando": TokenType.AND,
    "matawa": TokenType.OR,
    "nai": TokenType.NOT,
    "for": TokenType.FOR,
    "yomu_ln": TokenType.PRINTLN,
}
