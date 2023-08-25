import sys

ERROR = '\033[31m'
WARNING = '\033[33m'
ENDC = '\033[0m'


def throw_err(msg):
    print(f"{ERROR}{msg}{ENDC}", file=sys.stderr)
    sys.exit(1)
