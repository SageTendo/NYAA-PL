import sys

from src.utils.ErrorHandler import SUCCESS, ENDC


class Repl:
    def __init__(self, parser, interpreter):
        self.parser = parser
        self.interpreter = interpreter

    def run(self, dflags=None):
        print(f"{SUCCESS}Ohayo!!! (◕‿◕✿)\n"
              f"Welcome to the NYAA REPL! Type 'yamete()' to exit. (｡♥‿♥｡)\n{ENDC}")

        while True:
            line = self.handle_input()
            if len(line) == 0:
                continue

            try:
                AST = self.parser.parse_source(repl_input=line, dflags=dflags)

                res = self.interpreter.interpret(AST)
                if not res or res.label == 'null':
                    print()
                    continue

                if isinstance(res, list):
                    for r in res:
                        if r:
                            print(r, "\n")
                elif res:
                    print(res, "\n")
            except Exception as e:
                print(e.with_traceback(None), '\n', file=sys.stderr)

    @staticmethod
    def handle_input():
        try:
            line = str(input(">> "))
        except KeyboardInterrupt:
            print()
            exit(0)

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
