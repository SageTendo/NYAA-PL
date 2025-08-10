from enum import Enum, auto

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.Token import Token


class TokenType(Enum):
    """
    This class defines all the tokens that NYAA can parse.
    A series of helper functions are defined for the parser to
    use to figure how to handle a token it encounters.

    Tokens are assigned unique integer values using `enum.auto()`,
    and so IT IS IMPORTANT that the order of these tokens is maintained
    in order for the parser to understand which categories tokens
    belong to; ie. (BODY_STATEMENTS, CALLABLES, FACTORS,...)

    To figure out which group/parse_type a token falls under, the value
    must fall within the _begin_X_definition and _end_X_definition
    Example:
        - from _BEGIN_BODY_STATEMENT_DEFINITIONS to _END_BODY_STATEMENT_DEFINITIONS
        Encompasses a range of tokens that can be indicate body statements to be parsed.
    """

    NULL = auto()  # null token

    # Program start
    MAIN = auto()

    # ========================================================
    # STATEMENT DEFINITIONS
    # ========================================================
    _BEGIN_BODY_STATEMENT_DEFINITIONS = auto()
    RET = auto()
    DEF = auto()

    _BEGIN_CALLABLE_DEFINITIONS = auto()
    INPUT = auto()
    PRINT = auto()
    PRINTLN = auto()
    GET_CHAR = auto()
    STR_SPLIT = auto()
    LEN = auto()

    _BEGIN_FILE_IO_DEFINITIONS = auto()
    FILE_OPEN = auto()
    FILE_CLOSE = auto()
    FILE_READ = auto()
    FILE_READLINE = auto()
    FILE_WRITE = auto()
    FILE_WRITELINE = auto()
    _END_FILE_IO_DEFINITIONS = auto()
    _END_CALLABLE_DEFINITIONS = auto()

    _BEGIN_CONDITIONAL_STATEMENT_DEFINITION = auto()
    IF = auto()
    WHILE = auto()
    FOR = auto()
    _END_BODY_STATEMENT_DEFINITIONS = auto()
    ELIF = auto()
    ELSE = auto()
    CONTINUE = auto()
    BREAK = auto()
    _END_CONDITIONAL_STATEMENT_DEFINITION = auto()

    # ========================================================
    # OPERATOR DEFINITIONS
    # ========================================================
    _BEGIN_BINARY_OPERATOR_DEFINITIONS = auto()
    _BEGIN_ADDITIVE_OPERATOR_DEFINITIONS = auto()
    # Add
    PLUS = auto()
    MINUS = auto()
    _END_ADDITIVE_OPERATOR_DEFINITIONS = auto()

    # Multiplicative
    _BEGIN_MULTIPLICATIVE_OPERATOR_DEFINITIONS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()  # %
    _END_MULTIPLICATIVE_OPERATOR_DEFINITIONS = auto()

    # Relational
    _BEGIN_RELATIONAL_OPERATOR_DEFINITIONS = auto()
    EQ = auto()  # ==
    NEQ = auto()  # !=
    LT = auto()  # <
    GT = auto()  # >
    LTE = auto()  # <=
    GTE = auto()  # >=
    AND = auto()
    OR = auto()
    _END_RELATIONAL_OPERATOR_DEFINITIONS = auto()
    _BEGIN_POSTFIX_OPERATOR_DEFINITIONS = auto()
    # postfix operators
    UN_ADD = auto()  # ++
    UN_SUB = auto()  # --
    _END_POSTFIX_OPERATOR_DEFINITIONS = auto()
    _END_BINARY_OPERATOR_DEFINITIONS = auto()

    # ========================================================
    # FACTOR DEFINITIONS
    # ========================================================
    _BEGIN_FACTOR_DEFINITIONS = auto()
    # Types
    ID = auto()
    INT = auto()
    STR = auto()
    FLOAT = auto()
    BOOL = auto()
    # Booleans
    TRUE = auto()
    FALSE = auto()

    _BEGIN_UNARY_OPERATOR_DEFINITIONS = auto()
    # Negations
    NOT = auto()
    NEG = auto()  # -
    _END_UNARY_OPERATOR_DEFINITIONS = auto()
    LPAR = auto()  # (
    _END_FACTOR_DEFINITIONS = auto()

    # ========================================================
    # LITERAL DEFINITIONS
    # ========================================================
    _BEGIN_LITERAL_DEFINITIONS = auto()
    # Non-alphabetic operators
    ASSIGN = auto()
    FILE_EOF = auto()
    TO = auto()  # =>
    RPAR = auto()  # )
    SEMICOLON = auto()  # ;
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,
    COLON = auto()  # ::
    _END_LITERAL_DEFINITIONS = auto()

    ENDMARKER = auto()  # End of file
    ERR = auto()  # Lexer only

    @classmethod
    def statement_start(cls, token: "Token") -> bool:
        is_statement_start = token.type == TokenType.ID
        is_statement_start |= cls.token_within(
            token,
            cls._BEGIN_BODY_STATEMENT_DEFINITIONS,
            cls._END_BODY_STATEMENT_DEFINITIONS,
        )
        return is_statement_start

    @classmethod
    def conditional_stmt_start(cls, token: "Token") -> bool:
        return cls.statement_start(token) or (
            token.value < cls._END_CONDITIONAL_STATEMENT_DEFINITION.value
        )

    @classmethod
    def postfix(cls, token: "Token") -> bool:
        return cls.token_within(
            token,
            cls._BEGIN_POSTFIX_OPERATOR_DEFINITIONS,
            cls._END_POSTFIX_OPERATOR_DEFINITIONS,
        )

    @classmethod
    def unary(cls, token) -> bool:
        return cls.token_within(
            token,
            cls._BEGIN_UNARY_OPERATOR_DEFINITIONS,
            cls._END_UNARY_OPERATOR_DEFINITIONS,
        )

    @classmethod
    def expression(cls, token: "Token") -> bool:
        return cls.factor(token)

    @classmethod
    def term(cls, token: "Token") -> bool:
        return cls.factor(token)

    @classmethod
    def factor(cls, token: "Token") -> bool:
        return cls.token_within(
            token,
            TokenType._BEGIN_FACTOR_DEFINITIONS,
            TokenType._END_FACTOR_DEFINITIONS,
        )

    @classmethod
    def bin_op(cls, token: "Token") -> bool:
        return cls.rel_op(token) or cls.add_op(token) or cls.mul_op(token)

    @classmethod
    def rel_op(cls, token: "Token") -> bool:
        return cls.token_within(
            token,
            cls._BEGIN_RELATIONAL_OPERATOR_DEFINITIONS,
            cls._END_RELATIONAL_OPERATOR_DEFINITIONS,
        )

    @classmethod
    def add_op(cls, token: "Token") -> bool:
        return cls.token_within(
            token,
            cls._BEGIN_ADDITIVE_OPERATOR_DEFINITIONS,
            cls._END_ADDITIVE_OPERATOR_DEFINITIONS,
        )

    @classmethod
    def mul_op(cls, token: "Token") -> bool:
        return cls.token_within(
            token,
            cls._BEGIN_MULTIPLICATIVE_OPERATOR_DEFINITIONS,
            cls._END_MULTIPLICATIVE_OPERATOR_DEFINITIONS,
        )

    @classmethod
    def callable(cls, token: "Token") -> bool:
        return cls.token_within(
            token,
            TokenType._BEGIN_CALLABLE_DEFINITIONS,
            TokenType._END_CALLABLE_DEFINITIONS,
        )

    @classmethod
    def file_IO(cls, token: "Token") -> bool:
        return cls.token_within(
            token, cls._BEGIN_FILE_IO_DEFINITIONS, cls._END_FILE_IO_DEFINITIONS
        )

    @classmethod
    def assignment(cls, token: "Token") -> bool:
        return token.type in [TokenType.ASSIGN, TokenType.LBRACKET]

    @staticmethod
    def token_within(
        token: "Token",
        start_token_definition: "TokenType",
        end_token_definition: "TokenType",
    ):
        return start_token_definition.value < token.value < end_token_definition.value

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
    "f_open": TokenType.FILE_OPEN,
    "f_close": TokenType.FILE_CLOSE,
    "f_read": TokenType.FILE_READ,
    "f_readline": TokenType.FILE_READLINE,
    "f_write": TokenType.FILE_WRITE,
    "f_writeline": TokenType.FILE_WRITELINE,
    "f_EOF": TokenType.FILE_EOF,  # TODO: Is this being used?
    "asChar": TokenType.GET_CHAR,
    "split": TokenType.STR_SPLIT,
    "len": TokenType.LEN,
}
