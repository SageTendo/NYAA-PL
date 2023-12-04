import sys

from src.utils.ErrorHandler import SUCCESS, ENDC


class Repl:
    def __init__(self, parser, interpreter):
        self.parser = parser
        self.interpreter = interpreter

    def run(self, dflags=None):
        print(f"{SUCCESS}Ohayo!!! (◕‿◕✿)\n"
              f"Welcome to the Nyaa REPL! Type 'yamete()' to exit. (｡♥‿♥｡)\n{ENDC}")

        while True:
            line = self.handle_input()
            AST = self.parser.parse_source(repl_input=line, dflags=dflags)

            try:
                self.interpreter.interpret(AST)
            except Exception as e:
                print(e, '\n', file=sys.stderr)

    @staticmethod
    def handle_input():
        line = str(input("REPL> "))

        # Exit
        if line == "yamete()":
            exit(0)

        # Handle multiline input
        if line.endswith('{'):
            next_line = str(input())
            while not next_line.endswith('}'):
                line += next_line
                next_line = str(input())
            line += next_line
        return line
