from enum import Enum, auto


class TokenType(Enum):
    """Token types"""
    # Program start
    MAIN = auto()  # nyaa_main

    # Types
    INT = auto()  # inteja
    STR = auto()  # soturingu
    FLOAT = auto()  # furoto
    BOOL = auto()  # buru
    TRUE = auto()  # HAI
    FALSE = auto()  # IIE

    # Statements (Independent)
    VAR = auto()  # namae
    ID = auto()  # Identifier
    DEF = auto()  # kawaii
    IF = auto()  # if
    WHILE = auto()  # while
    FOR = auto()  # for
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
    RANGE = auto()  # from
    EXCEPT = auto()  # gome

    # Non-alphabetic operators
    TO = auto()  # =>
    LPAR = auto()  # (
    RPAR = auto()  # )
    SEMICOLON = auto()  # ;
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    COMMA = auto()  # ,

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
    def body_start(cls, token):
        return token.type in [
            TokenType.VAR, TokenType.DEF, TokenType.PASS, TokenType.BREAK,
            TokenType.CONTINUE, TokenType.RET, TokenType.NOT, TokenType.NEG,
            TokenType.ID, TokenType.FOR, TokenType.WHILE, TokenType.IF,
            TokenType.PRINT, TokenType.INPUT, TokenType.TRY
        ]

    @classmethod
    def unary(cls, token):
        return token.type in [
            TokenType.NEG, TokenType.NOT
        ]

    @classmethod
    def conditional(cls, token):
        pass

    @classmethod
    def expression(cls, token):
        return token.type in [TokenType.NEG, TokenType.LPAR] or cls.term(token)

    @classmethod
    def term(cls, token):
        return token.type in [
            TokenType.ID, TokenType.INT, TokenType.STR,
            TokenType.FLOAT, TokenType.TRUE, TokenType.FALSE
        ]

    def __str__(self):
        return self.name

    @classmethod
    def bin_op(cls, token):
        return token.type in [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
            TokenType.DIVIDE, TokenType.EQ, TokenType.NEQ, TokenType.LT,
            TokenType.GT, TokenType.LTE, TokenType.GTE, TokenType.AND,
            TokenType.OR
        ]
