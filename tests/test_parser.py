import os.path
import sys

from src.Lexer import Lexer
from src.Parser import Parser
from src.utils.Constants import SUCCESS, ENDC, ERROR
from tests import BaseTest


class TestParser(BaseTest):
    def setUp(self):
        self.lexer: Lexer = Lexer()
        self.parser: Parser = Parser(lexer=self.lexer)

    def test_parser(self):
        self.print_header("Parser")
        test_dir = os.path.join(self.test_dir, "interpreter/in/")
        for file in os.listdir(test_dir):
            if not file.endswith(".ny"):
                continue

            try:
                print(f"[Parser] Running test on: {file}")
                self.parser.parse_source(filepath=test_dir + file)

                print(f"{SUCCESS}  Passed{ENDC}")
            except Exception as e:
                print(f"{ERROR}  Failed{ENDC}", e, file=sys.stderr)
                self.fail()
