import argparse

from src.Parser import Parser
from src.utils.ErrorHandler import ERROR, ENDC


def parse_args():
    """
    Custom arg parser for parsing CLI arguments
    @return:
    """

    class CustomArgParser(argparse.ArgumentParser):
        def error(self, message):
            if 'src' in message:
                print(f"{ERROR}No program file was provided...\n")
            print(f"Usage: python3 {__file__} <PROGRAM> {ENDC}")
            exit(1)

    arg_parser = CustomArgParser()
    arg_parser.add_argument("src", type=str, help="The source file to translate")
    arg_parser.add_argument(
        '-l', '--lexer', action='store_true', default=False, help="Verbose mode for the lexer")
    arg_parser.add_argument(
        '-p', '--parser', action='store_true', default=False, help="Verbose mode for the parser")

    return arg_parser.parse_args()


if __name__ == '__main__':
    # Args parsing
    args = parse_args()

    # Parse source code
    parser = Parser()
    dflags = {"lexer": args.lexer, "parser": args.parser}
    AST = parser.parse(args.src, dflags)
    print(AST)
