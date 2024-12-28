import readline
import sys

from src.core.RuntimeObject import RunTimeObject
from src.utils.Constants import SUCCESS, ENDC


class Repl:
    def __init__(self, parser, interpreter):
        self.parser = parser
        self.interpreter = interpreter
        self.autocompletion_cmds = None

        # Shell confiurations
        readline.set_auto_history(False)
        readline.set_history_length(1000)
        readline.parse_and_bind("set blink-matching-paren on")

    def run(self):
        print(
            f"{SUCCESS}Ohayo!!! (◕‿◕✿)\n"
            f"Welcome to the NYAA REPL! Type 'jaa ne' to exit. (｡♥‿♥｡)\n{ENDC}"
        )

        while True:
            line = self.handle_input()
            if not line:
                continue
            self.execute(line)

    @staticmethod
    def handle_input():
        try:
            line = str(input(">> "))
        except KeyboardInterrupt:
            print()
            exit(1)

        if line.lower() == "jaa ne":
            exit(0)

        # Handle multiline input
        if line.endswith("{"):
            next_line = str(input())

            while not next_line.endswith("}"):
                line += next_line
                next_line = str(input())
            line += next_line
        return line if len(line) > 0 else None

    def execute(self, line):
        try:
            AST = self.parser.parse_source(repl_input=line)
            res = self.interpreter.interpret(AST)

            # Add successful commands to history
            readline.add_history(line)
            if not res or res.label == "null":
                print()
                return

            # Print the result
            if isinstance(res, list):
                for r in res:
                    print(r.value, "\n") if r and isinstance(r, RunTimeObject) else None
            elif isinstance(res, RunTimeObject):
                print(res.value, "\n")
        except Exception as e:
            print(e.with_traceback(None), "\n", file=sys.stderr)
