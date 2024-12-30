import random
from enum import Enum

from src.utils.Constants import ERROR, WARNING, SUCCESS, ENDC


class ErrorType(Enum):
    TYPE = "Type Error (型エラー)"
    RUNTIME = "Runtime Error (ランタイムエラー)"
    RECURSION = "Recursion Error (再帰エラー)"
    NOT_IMPLEMENTED = "Not Implemented Error (未実装エラー)"


class LexerError(Exception):

    def __init__(self, message: str, line_number: int, col_number: int):
        self.message = (
            f"{WARNING}{emoji()}\n"
            f"Lexical Error (字句エラー): "
            f"{ERROR}{message} at position {WARNING}{line_number}:{col_number}{ENDC}"
        )
        super().__init__(self.message)


class ParserError(Exception):

    def __init__(self, message: str, line_number: int, col_number: int):
        self.message = (
            f"{WARNING}{emoji()}\n"
            f"Syntax Error (構文エラー): {ERROR}{message} at position {WARNING}{line_number}:{col_number}{ENDC}"
        )
        super().__init__(self.message)


class InterpreterError(Exception):

    def __init__(
        self, err_tpye: ErrorType, message: str, start_pos: tuple, end_pos: tuple
    ):
        start_line_number, start_col_number = start_pos
        end_line_number, end_col_number = end_pos

        self.message = (
            f"{WARNING}{emoji()}\n"
            f"{err_tpye.value}: {ERROR}{message}{ERROR} "
            f"at position {WARNING}{start_line_number}:{start_col_number} "
            f"to {end_line_number}:{end_col_number}{ENDC}"
        )
        super().__init__(self.message)


# ----------------------------------------------------------------------------------------------------------------------
# Syntax errors
def throw_unexpected_token_err(token_type, expected_type, line_number, col_number):
    """
    Throws an error when an unexpected token is parsed
    @param token_type   : The unexpected token type
    @param expected_type: The expected token type to be parsed
    @param line_number  : The line number of the unexpected token
    @param col_number   : The column number of the unexpected token
    """
    raise ParserError(
        f"Unexpected token {WARNING}'{token_type}'\n"
        f"Expected {SUCCESS}{expected_type}{ERROR}",
        line_number,
        col_number,
    )


# ----------------------------------------------------------------------------------------------------------------------
# Runtime Errors
def throw_invalid_operation_err(lhs, op, rhs, start_pos, end_pos):
    """
    Throws an exception when an invalid operation is performed
    @param lhs: LHS value
    @param op: operator
    @param rhs: RHS value
    @param start_pos: The starting position of the expression
    @param end_pos: The ending position of the expression
    """
    raise InterpreterError(
        ErrorType.TYPE,
        f"Invalid operation {WARNING}'{lhs} {op} {rhs}'",
        start_pos,
        end_pos,
    )


def throw_unary_type_err(operator, operand_label, start_pos, end_pos):
    """
    Throws an error when an unsupported unary type is parsed
    @param operator: The unary operator node
    @param operand_label: The label of the operand
    @param start_pos: The starting position of the expression
    @param end_pos: The ending position of the expression
    """
    raise InterpreterError(
        ErrorType.RUNTIME,
        f"Can't apply unary operator "
        f"{WARNING}'{operator}'{ERROR} on a {WARNING}'{operand_label}'",
        start_pos,
        end_pos,
    )


# ----------------------------------------------------------------------------------------------------------------------
# Basic Errors
def warning_msg(msg):
    """
    Displays warning to console
    @param msg:
    """
    return f"{WARNING}{msg}{ENDC}"


def success_msg(msg):
    """
    Display info to console
    @param msg:
    """
    return f"{SUCCESS}{msg}{ENDC}"


def emoji():
    """
    Returns a random emoji for the error message
    """
    kawaii_emoticons = [
        # Sad Kawaii Emojis
        "(-_-)",
        "(つω`｡)",
        "(；⌣̀_⌣́)",
        "╥﹏╥",
        "(⌣́_⌣̀)",
        "(∩︵∩)",
        "(◡﹏◡✿)",
        "(✿◠‿◠)",
        # Mad Kawaii Emojis
        "ಠ_ಠ",
        "(¬_¬)",
        "(╯°□°）╯︵ ┻━┻",
        "щ(ºДºщ)",
        "ಠ益ಠ",
        "(*`益´*)",
        "(ノಠ益ಠ)ノ彡┻━┻",
        "ヽ(｀Д´)ﾉ",
    ]
    return kawaii_emoticons[random.randint(0, len(kawaii_emoticons) - 1)]
