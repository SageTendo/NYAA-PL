import os.path
import sys
from pathlib import Path

from src.Lexer import Lexer
from src.core.Token import Token
from src.core.Types import TokenType
from src.utils.Constants import WARNING, SUCCESS, ENDC, ERROR
from tests import BaseTest


class TestLexer(BaseTest):
    def setUp(self):
        self.lexer: Lexer = Lexer()

    def test_lexer(self):
        self.print_header("Lexer")
        test_dir = os.path.join(self.test_dir, "lexer/")
        for file in os.listdir(test_dir):
            if not file.endswith(".lex"):
                continue

            try:
                print(f"[Lexer] Running test on: {file}")
                self.lexer.analyze_src_file(Path(test_dir + file))

                token = Token()
                while token.type != TokenType.ENDMARKER:
                    token = self.lexer.get_token()

                print(f"{SUCCESS}  Passed{ENDC}")
            except Exception as e:
                print(f"{ERROR}  Failed{ENDC}")
                print(e, file=sys.stderr)
                self.fail()

    def test_lexer_errors(self):
        self.print_header("Lexer Errors")
        test_dir = os.path.join(self.test_dir, "errors/lexer/")
        for file in os.listdir(test_dir):
            if not file.endswith(".lex"):
                continue

            # Load expected output
            output_file = file.replace(".lex", ".out")
            with open(os.path.join(test_dir, output_file)) as f:
                expected = f.read()

            # Skip test if no expected output
            if expected is None:
                print(f"{WARNING}  [Skipped] No expected output found for {file}{ENDC}")
                continue

            try:
                print(f"[Lexer Error] Running test on: {file}")
                self.lexer.analyze_src_file(Path(test_dir + file))

                token = Token()
                while token.type != TokenType.ENDMARKER:
                    token = self.lexer.get_token()

                self.fail()
            except Exception as e:
                expected = expected.strip().lower()
                e = str(e).lower()
                if expected not in e and len(expected) > 0:
                    print(f"{ERROR}  Failed{ENDC}", e, file=sys.stderr)
                    self.fail(f"EXPECTED:\n    {expected}\nACTUAL:\n    {e}")

                print(f"{SUCCESS}  Passed{ENDC}")
            finally:
                self.lexer.__init__()
