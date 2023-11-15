from enum import Enum, auto


class TokenType(Enum):
    """Token types"""
    ID = auto()  # Identifier

    # Keywords
    MAIN = auto()  # nyaa_main
    PRINT = auto()  # printu
    INPUT = auto()  # ohayo
    ASSIGN = auto()  # asain

    WHILE = auto()  # while
    FOR = auto()  # for
    IF = auto()  # if
    ELSE = auto()  # else
    ELIF = auto()  # elif
    RANGE = auto()  # from
    PASS = auto()  # pasu
    BREAK = auto()  # yamete
    CONTINUE = auto()  # motto

    DEF = auto()  # kawaii
    TRY = auto()  # ganbatte
    EXCEPT = auto()  # gome

    INT = auto()  # inteja
    STR = auto()  # soturingu
    FLOAT = auto()  # furoto
    BOOL = auto()  # buru
    RET = auto()  # sayonara
    TRUE = auto()  # HAI
    FALSE = auto()  # IIE

    # Non-alphabetic operators
    TO = auto()  # =>
    LPAR = auto()  # (
    RPAR = auto()  # )
    SEMICOLON = auto()  # ;
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    COMMA = auto()  # ,
    # LBRACKET = auto()  # [
    # RBRACKET = auto()  # ]
    # COLON = auto()  # :
    # TYPE_ASSIGN = auto()  # ::

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

    # End marker
    ENDMARKER = auto()  # End of file

    def __str__(self):
        return self.name
