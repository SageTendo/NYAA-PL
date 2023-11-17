import sys

ERROR = '\033[91m'
WARNING = '\033[33m'
SUCCESS = '\033[92m'
ENDC = '\033[0m'


def throw_unexpected_token_err(token_type, expected_type, line_number, col_number):
    throw_err(
        f"{__file__}: "
        f"Unexpected token found at {line_number}:{col_number()}.\n"
        f"Expected {expected_type}, but got {token_type} instead..."
    )


def throw_err(msg):
    """
    Simple error handling with coloured text
    @param msg: The message to display to the console
    """
    print(f"{ERROR}{msg}{ENDC}", file=sys.stderr)
    sys.exit(1)


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
