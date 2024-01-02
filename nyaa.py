import argparse
import sys

from src.Interpreter import Interpreter
from src.Parser import Parser
from src.Repl import Repl


def parse_args():
    """
    Custom arg parser for parsing CLI arguments
    @return:
    """

    arg_parser = argparse.ArgumentParser()
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        arg_parser.add_argument("src", type=str, help="The source file to translate")

    arg_parser.add_argument(
        '-l', '--lexer', action='store_true', default=False, help="Verbose mode for the lexer")
    arg_parser.add_argument(
        '-p', '--parser', action='store_true', default=False, help="Verbose mode for the parser")
    arg_parser.add_argument(
        '-i', '--interpreter', action='store_true', default=False, help="Verbose mode for the interpreter")
    return arg_parser.parse_args()


if __name__ == '__main__':
    # Args parsing
    args = parse_args()
    parser = Parser()
    interpreter = Interpreter()
    interpreter.verbose(args.interpreter)

    dflags = {"lexer": args.lexer, "parser": args.parser}
    if 'src' not in args:
        # REPL mode
        Repl(parser, interpreter).run(dflags=dflags)
    else:
        # Parse source code
        AST = parser.parse_source(source_path=args.src, dflags=dflags)
        parser = None

        # Start interpreter
        interpreter.interpret(AST)
