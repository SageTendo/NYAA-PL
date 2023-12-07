import sys

ERROR = '\033[91m'
WARNING = '\033[33m'
SUCCESS = '\033[92m'
ENDC = '\033[0m'


# ----------------------------------------------------------------------------------------------------------------------
# Lexical Errors

def throw_string_length_err(line_number, col_number):
    """
    Throws an error when a string exceeds the maximum length allowed
    @param line_number:  The line number of the string
    @param col_number :  The column number of the string
    """
    raise __throw_err(f"Lexical error\n"
                      f"String too long at {line_number}:{col_number}")


def throw_unexpected_char_err(char, line_number, col_number):
    """
    Throws an error when an unexpected character is found in the program
    @param char:        The unexpected character
    @param line_number:  The line number of the unexpected character
    @param col_number :  The column number of the unexpected character
    """
    raise __throw_err(f"Lexical error\n"
                      f"Unexpected character {WARNING}'{char}'{ERROR} at position {WARNING}{line_number}:{col_number}{ENDC}")


def throw_unexpected_eof_err(line_number, col_number):
    """
    Throws an error when an unexpected end of file character is found in the program
    @param line_number:  The line number of the unexpected end of file
    @param col_number :  The column number of the unexpected end of file
    """
    raise __throw_err(f"Lexical error\n"
                      f"Unterminated string at {line_number}:{col_number}")


def throw_unexpected_escape_char_err(char, line_number, col_number):
    """
    Throws an error when an unexpected escape character is found in the program
    @param char       : The unexpected escape character
    @param line_number: The line number of the unexpected escape character
    @param col_number : The column number of the unexpected escape character
    """
    raise __throw_err(f"Lexical error\n"
                      f"Unexpected escape character {WARNING}'{char}'{ERROR} at position {WARNING}{line_number}:{col_number}{ENDC}")


def throw_non_printable_char_err(char, line_number, col_number):
    """
    Throws an error when a non-printable ascii character is found in the program
    @param char       : The non-printable ascii character
    @param line_number: The line number of the non-printable ascii character
    @param col_number : The column number of the non-printable ascii character
    """
    raise __throw_err(f"Lexical error\n"
                      f"Non-printable ascii character with code: "
                      f"{ord(char)} at {line_number}:{col_number}")


def throw_identifier_length_err(line_number, col_number):
    """
    Throws an error when an identifier exceeds the maximum length allowed
    @param line_number: The line number of the identifier
    @param col_number : The column number of the identifier
    """
    raise __throw_err(f"Lexical error\n"
                      f"Identifier length exceeded at position {WARNING}{line_number}:{col_number}{ENDC}")


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
    raise __throw_err(f"Syntax error\n"
                      f"Unexpected token found at {line_number}:{col_number}.\n"
                      f"Expected {SUCCESS}{expected_type}{ERROR}, but found {WARNING}{token_type}{ERROR}")


# ----------------------------------------------------------------------------------------------------------------------
# Semantic errors

def throw_unary_type_err(operator, operand):
    """
    Throws an error when an unsupported unary type is parsed
    @param operator: The unary operator node
    @param operand: The unary operand node
    """
    raise __throw_err(f"Sematic error\n"
                      f"Unsupported unary type for {operator}: {operand}")


def throw_invalid_operation_err(lhs, op, rhs):
    """
    Throws an exception when an invalid operation is performed
    @param lhs: LHS value
    @param op: operator
    @param rhs: RHS value
    """
    raise __throw_err("Type error\n"
                      f"Invalid operation {lhs} {op} {rhs}")


# ----------------------------------------------------------------------------------------------------------------------
# Basic Errors


def __throw_err(msg):
    """
    Simple error handling with coloured text
    @param msg: The message to display to the console
    """
    return Exception(f"{ERROR}{msg}{ENDC}")


def warning_msg(msg):
    """
    Displays warning to console
    @param msg:
    """
    print(f"{WARNING}{msg}{ENDC}", file=sys.stderr)


def success_msg(msg):
    """
    Display info to console
    @param msg:
    """
    print(f"{SUCCESS}{msg}{ENDC}")
