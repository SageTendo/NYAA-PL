import argparse
import sys

from src.Interpreter import Interpreter
from src.Lexer import Lexer
from src.Parser import Parser
from src.Repl import Repl


def parse_args():
    """Custom arg parser for parsing CLI arguments"""
    arg_parser = argparse.ArgumentParser()
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        arg_parser.add_argument("src", type=str, help="The source file to translate")

    arg_parser.add_argument(
        "-l",
        "--lexer",
        action="store_true",
        default=False,
        help="Verbose mode for the lexer",
    )
    arg_parser.add_argument(
        "-p",
        "--parser",
        action="store_true",
        default=False,
        help="Verbose mode for the parser",
    )
    arg_parser.add_argument(
        "-i",
        "--interpreter",
        action="store_true",
        default=False,
        help="Verbose mode for the interpreter",
    )
    return arg_parser.parse_args()


def main():
    args = parse_args()
    lexer = Lexer(verbose=args.lexer)
    parser = Parser(lexer=lexer, verbose=args.parser)
    interpreter = Interpreter(verbose=args.interpreter)

    if "src" not in args:
        Repl(parser, interpreter).run()
    else:
        AST = parser.parse_source(source_path=args.src)
        interpreter.interpret(AST)


if __name__ == "__main__":
    main()
