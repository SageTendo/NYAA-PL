import sys

ERROR = '\033[91m'
WARNING = '\033[33m'
SUCCESS = '\033[92m'
ENDC = '\033[0m'


def throw_unexpected_char_err(char, line_number, col_number):
    throw_err(
        f"{__file__}:\n"
        f"Unexpected character {WARNING}'{char}'{ERROR} at position {WARNING}{line_number}:{col_number}{ENDC}"
    )


def throw_unexpected_token_err(token_type, expected_type, line_number, col_number):
    throw_err(
        f"{__file__}: "
        f"Unexpected token found at {line_number}:{col_number}.\n"
        f"Expected {SUCCESS}{expected_type}{ERROR}, but found {WARNING}{token_type}{ERROR}"
    )


def throw_err(msg):
    """
    Simple error handling with coloured text
    @param msg: The message to display to the console
    """
    print(f"{ERROR}{msg}{ENDC}", file=sys.stderr)
    exit(1)


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
