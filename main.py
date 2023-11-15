import argparse

from src.utils.ErrorHandler import throw_err, ERROR, ENDC
from src.Lexer import Lexer
from src.Token import Token
from src.Types import TokenType


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
    return arg_parser.parse_args()


lexer = Lexer()
if __name__ == '__main__':
    # Args parsing
    args = parse_args()

    # Get source file
    lexer.load_src_file(args.src)

    # Processing
    tkn = Token()  # placeholder token
    while tkn.type != TokenType.ENDMARKER:
        tkn = lexer.get_token()
        if tkn.type is None:
            line = lexer.get_line_number()
            col = lexer.get_col_number()
            char = lexer.get_last_read()
            throw_err(f"Unrecognized symbol {char} found at {line}:{col}...")
            exit(1)
        print(tkn)
