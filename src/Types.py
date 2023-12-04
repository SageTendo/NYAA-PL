from enum import Enum, auto


class TokenType(Enum):
    """Token types"""
    # Program start
    MAIN = auto()  # uWu_nyaa

    # Types
    INT = auto()  # inteja
    STR = auto()  # soturingu
    FLOAT = auto()  # furoto
    BOOL = auto()  # buru
    TRUE = auto()  # HAI
    FALSE = auto()  # IIE

    # Statements (Independent)
    ID = auto()  # Identifier
    DEF = auto()  # kawaii
    IF = auto()  # if
    WHILE = auto()  # while
    TRY = auto()  # ganbatte
    INPUT = auto()  # ohayo
    PRINT = auto()  # printu
    # Breaks
    PASS = auto()  # pasu
    CONTINUE = auto()  # motto
    BREAK = auto()  # yamete
    RET = auto()  # sayonara

    # Dependent statements
    ELIF = auto()  # elif
    ELSE = auto()  # else
    ASSIGN = auto()  # asain
    EXCEPT = auto()  # gome

    # Non-alphabetic operators
    TO = auto()  # =>
    LPAR = auto()  # (
    RPAR = auto()  # )
    SEMICOLON = auto()  # ;
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    COMMA = auto()  # ,
    PERIOD = auto()  # .

    # Binary operators
    PLUS = auto()  # purasu
    MINUS = auto()  # mainasu
    MULTIPLY = auto()  # purodukuto
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
    def statement_start(cls, token):
        return token.type in [
            TokenType.PASS, TokenType.RET,
            TokenType.ID, TokenType.WHILE, TokenType.IF,
            TokenType.PRINT, TokenType.INPUT, TokenType.TRY
        ]

    @classmethod
    def postfix(cls, token):
        return token.type in [
            TokenType.UN_ADD, TokenType.UN_SUB
        ]

    @classmethod
    def unary(cls, token):
        return token.type in [
            TokenType.NEG, TokenType.NOT
        ]

    @classmethod
    def expression(cls, token):
        return cls.factor(token)

    @classmethod
    def term(cls, token):
        return cls.factor(token)

    @classmethod
    def factor(cls, token):
        return token.type in [
            TokenType.ID, TokenType.INT, TokenType.STR,
            TokenType.FLOAT, TokenType.TRUE, TokenType.FALSE,
            TokenType.LPAR, TokenType.NEG, TokenType.NOT
        ]

    @classmethod
    def bin_op(cls, token):
        return cls.rel_op(token) or cls.add_op(token) or cls.mul_op(token)

    @classmethod
    def rel_op(cls, token):
        return token.type in [
            TokenType.EQ, TokenType.NEQ, TokenType.LT,
            TokenType.GT, TokenType.LTE, TokenType.GTE
        ]

    @classmethod
    def add_op(cls, token):
        return token.type in [
            TokenType.PLUS, TokenType.MINUS, TokenType.OR
        ]

    @classmethod
    def mul_op(cls, token):
        return token.type in [
            TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.AND
        ]

    @classmethod
    def callable(cls, token):
        return token.type in [
            TokenType.ID, TokenType.PRINT, TokenType.INPUT
        ]

    def __str__(self):
        return self.name
