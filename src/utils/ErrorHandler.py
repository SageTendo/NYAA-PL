import sys

ERROR = '\033[31m'
WARNING = '\033[33m'
ENDC = '\033[0m'


def throw_err(msg):
    """
    Simple error handling with coloured text
    @param msg: The message to display to the console
    """
    print(f"{ERROR}{msg}{ENDC}", file=sys.stderr)
    sys.exit(1)
