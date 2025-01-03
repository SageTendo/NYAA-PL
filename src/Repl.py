import readline
import sys

from src.Interpreter import Interpreter
from src.Parser import Parser
from src.core.RuntimeObject import RunTimeObject
from src.utils.Constants import SUCCESS, ENDC


class Repl:
    def __init__(self, parser: Parser, interpreter: Interpreter):
        self.parser = parser
        self.interpreter = interpreter
        self.autocompletion_cmds = None

        # Shell confiurations
        readline.set_auto_history(False)
        readline.set_history_length(1000)
        readline.parse_and_bind("set blink-matching-paren on")

    def run(self) -> None:
        """Starts the REPL"""
        print(
            f"{SUCCESS}Ohayo!!! (◕‿◕✿)\n"
            f"Welcome to the NYAA REPL! Type 'jaa ne' to exit. (｡♥‿♥｡)\n{ENDC}"
        )

        while True:
            line = self.handle_input()
            if not line:
                continue
            self.interpret(line)

    @staticmethod
    def handle_input() -> str:
        """Handles input from the user"""
        try:
            line = str(input(">> ")).strip()
        except (KeyboardInterrupt, EOFError):
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
        return line

    def interpret(self, line: str) -> None:
        """Parses and interprets input from the user"""
        try:
            AST = self.parser.parse_repl(repl_input=line)
            if not AST:  # Empty input
                return

            res = self.interpreter.interpret(AST)
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
