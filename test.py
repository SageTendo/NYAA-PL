import os.path
import subprocess
import sys
import unittest
from unittest import TestCase

from src.Interpreter import Interpreter
from src.Lexer import Lexer
from src.Parser import Parser
from src.core.Token import Token
from src.core.Types import TokenType
from src.utils.Constants import WARNING, SUCCESS, ENDC


class TestNyaa(TestCase):
    test_dir = os.path.dirname(__file__) + "/tests/"

    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.interpreter = Interpreter()

    def tearDown(self):
        self.lexer = None
        self.parser = None
        self.Interpreter = None

    def test_lexer(self):
        header = "Testing Lexer"
        print(header)
        print(f"-" * len(header))

        test_dir = os.path.join(self.test_dir, "lexer/")
        for file in os.listdir(test_dir):
            print(f"[Lexer] Running test on: {file}")

            try:
                self.lexer.analyze_src_file(test_dir + file)

                token = Token()
                while token.type != TokenType.ENDMARKER:
                    token = self.lexer.get_token()
                    print(" ", token)

                print(f"{SUCCESS}  Passed{ENDC}")
            except Exception as e:
                print(e, file=sys.stderr)
                self.fail()

    def test_parser(self):
        header = "Testing Parser"
        print(header)
        print(f"-" * len(header))

        test_dir = os.path.join(self.test_dir, "parser/")
        for file in os.listdir(test_dir):
            print(f"[Parser] Running test on: {file}")

            try:
                self.parser.parse_source(source_path=test_dir + file, dflags={"parser": True})
                print(f"{SUCCESS}  Passed{ENDC}\n")
            except Exception as e:
                print(e, file=sys.stderr)
                self.fail()

    def test_interpreter(self):
        header = "Testing Interpreter"
        print(header)
        print(f"-" * len(header))

        interpreter_dir = os.path.join(self.test_dir, "interpreter/")
        input_dir = os.path.join(interpreter_dir, "in/")
        output_dir = os.path.join(interpreter_dir, "out/")

        failed = False
        for file in os.listdir(input_dir):
            print(f"[Interpreter] Running test on: {file}")

            out_file = os.path.join(output_dir, file.replace(".ny", ".out"))
            try:
                f = open(out_file, "r")
                expected = f.read().strip().replace(' ', '')
                f.close()
            except FileNotFoundError:
                print(f"{WARNING}  No output file{ENDC}")
                print(f"{WARNING}  Skipped{ENDC}")
                continue

            proc = subprocess.run(
                ["python3", "nyaa.py", input_dir + file],
                capture_output=True,
                text=True
            )

            res = proc.stdout.strip().replace(' ', '')
            if res == expected and proc.returncode == 0:
                print(f"{SUCCESS}  Passed{ENDC}")
            else:
                expected_header = "EXPECTED OUTPUT:"
                print(f"{WARNING}{expected_header}", f"-" * len(expected_header))
                print(f"{expected}{ENDC}\n")

                actual_header = "ACTUAL OUTPUT:"
                print(f"{WARNING}{actual_header}", f"-" * len(actual_header))
                if proc.stderr:
                    print(f"{WARNING}{proc.stderr.strip()}{ENDC}")
                else:
                    print(f"{WARNING}{res.strip()}{ENDC}")
                failed = True

        if failed:
            self.fail()


if __name__ == '__main__':
    unittest.main()
