import os.path
import subprocess
import sys
import unittest
from pathlib import Path
from random import randint, choice
from unittest import TestCase

from src.Interpreter import Interpreter
from src.Lexer import Lexer
from src.Parser import Parser
from src.core.Token import Token
from src.core.Types import TokenType
from src.utils.Constants import WARNING, SUCCESS, ENDC, ERROR


class TestNyaa(TestCase):
    test_dir = os.path.dirname(__file__) + "/tests/"

    def setUp(self):
        self.lexer: Lexer = Lexer()
        self.parser: Parser = Parser(lexer=self.lexer)
        self.interpreter: Interpreter = Interpreter()
        self.num_random_tests = 25000

    def tearDown(self):
        print("", flush=True)

    @staticmethod
    def print_header(header):
        header = f"Testing {header}"
        print("#" * len(header))
        print(header)
        print("#" * len(header), flush=True)

    def test_lexer(self):
        self.print_header("Lexer")
        test_dir = os.path.join(self.test_dir, "lexer/")
        for file in os.listdir(test_dir):
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

    def test_parser(self):
        self.print_header("Parser")
        test_dir = os.path.join(self.test_dir, "interpreter/in/")
        for file in os.listdir(test_dir):
            try:
                print(f"[Parser] Running test on: {file}")
                self.parser.parse_source(filepath=test_dir + file)

                print(f"{SUCCESS}  Passed{ENDC}")
            except Exception as e:
                print(f"{ERROR}  Failed{ENDC}", e, file=sys.stderr)
                self.fail()

    def test_interpreter(self):
        self.print_header("Interpreter")
        interpreter_dir = os.path.join(self.test_dir, "interpreter/")
        input_dir = os.path.join(interpreter_dir, "in/")
        output_dir = os.path.join(interpreter_dir, "out/")

        failed = False
        for file in os.listdir(input_dir):
            out_file = os.path.join(output_dir, file.replace(".ny", ".out"))

            # Load expected output
            try:
                with open(out_file, "r") as f:
                    expected = f.read().strip().replace(" ", "")
            except FileNotFoundError:
                print(f"{WARNING}  [Skipped] No expected output found for {file}{ENDC}")
                continue

            print(f"[Interpreter] Running test on: {file}")
            proc = subprocess.run(
                ["python3", "nyaa.py", input_dir + file], capture_output=True, text=True
            )

            # Compare outputs
            res = proc.stdout.strip().replace(" ", "")
            if res == expected and proc.returncode == 0:
                print(f"{SUCCESS}  Passed{ENDC}")
            else:
                expected_header = "EXPECTED OUTPUT:"
                print(f"{WARNING}{expected_header}", "-" * len(expected_header))
                print(f"{expected}{ENDC}")

                actual_header = "ACTUAL OUTPUT:"
                print(f"{WARNING}{actual_header}", "-" * len(actual_header))
                if proc.stderr:
                    print(f"{WARNING}{proc.stderr.strip()}{ENDC}")
                else:
                    print(f"{WARNING}{res.strip()}{ENDC}")
                failed = True

        if failed:
            self.fail()

    def test_interpreter_errors(self):
        self.print_header("Interpreter Errors")
        test_dir = os.path.join(self.test_dir, "errors/interpreter/")
        for file in os.listdir(test_dir):
            if not file.endswith(".ny"):
                continue

            # Load expected output
            output_file = file.replace(".ny", ".out")
            with open(os.path.join(test_dir, output_file)) as f:
                expected = f.read()

            # Skip test if no expected output
            if expected is None:
                print(f"{WARNING}  [Skipped] No expected output found for {file}{ENDC}")
                continue

            print(f"[Interpreter Error] Running test on: {file}")
            proc = subprocess.run(
                ["python3", "nyaa.py", test_dir + file], capture_output=True, text=True
            )

            # Compare outputs
            result = str(proc.stderr).lower().strip()
            expected = expected.lower().strip()
            if expected not in result and len(expected) > 0:
                print(f"{ERROR}  Failed{ENDC}")
                self.fail(f"EXPECTED:\n    {expected}\nACTUAL:\n    {proc.stderr}")

            print(f"{SUCCESS}  Passed{ENDC}")

    def test_operator_precedence_expressions(self):
        self.print_header("Operator Precedence Expressions")
        operators = [
            ("purasu", "+"),
            ("mainasu", "-"),
            ("purodakuto", "*"),
            ("supuritto", "/"),
        ]

        start = -sys.maxsize - 1
        end = sys.maxsize
        for _ in range(self.num_random_tests):
            # Generate operands
            a = randint(start, end)
            b = randint(start, end)
            c = randint(start, end)
            d = randint(start, end)
            e = randint(start, end)
            f = randint(start, end)

            # Generate operators
            op1 = choice(operators)
            op2 = choice(operators)
            op3 = choice(operators)

            # Generate expressions
            repl_input = (
                f"{a} {op1[0]} {b} {op2[0]} {c} {op3[0]} {d} {op1[0]} {e} {op2[0]} {f}"
            )
            eval_input = (
                f"{a} {op1[1]} {b} {op2[1]} {c} {op3[1]} {d} {op1[1]} {e} {op2[1]} {f}"
            )
            try:
                expected = eval(eval_input)
                ast = self.parser.parse_repl(repl_input=repl_input)
                result = self.interpreter.interpret(ast)

                if result.value != expected:
                    print(f"{ERROR}   Failed{ENDC}")
                    self.fail(
                        f"EXPRESSION:\n"
                        f"    {eval_input}\n"
                        f"EXPECTED RESULT= {expected}\n"
                        f"ACTUAL RESULT=  {result.value}\n"
                    )
            except ZeroDivisionError:
                continue
            except Exception as e:
                print(e, file=sys.stderr)
                assert False

        print(f"{SUCCESS}  Passed{ENDC}")

    def test_prioritized_expressions(self):
        self.print_header("Prioritized Expressions")
        operators = [
            ("purasu", "+"),
            ("mainasu", "-"),
            ("purodakuto", "*"),
            ("supuritto", "/"),
            ("ando", "and"),
            ("matawa", "or"),
        ]

        start = -sys.maxsize - 1
        end = sys.maxsize
        for _ in range(self.num_random_tests // 2):
            # Generate operands
            a = randint(start, end)
            b = randint(start, end)
            c = randint(start, end)
            d = randint(start, end)

            # Generate operators
            op1 = choice(operators)
            op2 = choice(operators)
            op3 = choice(operators)

            # Generate expressions
            repl_input = f"({a} {op1[0]} {b}) {op2[0]} ({c} {op3[0]} {d})"
            eval_input = f"({a} {op1[1]} {b}) {op2[1]} ({c} {op3[1]} {d})"

            try:
                expected = eval(eval_input)
                ast = self.parser.parse_repl(repl_input=repl_input)
                result = self.interpreter.interpret(ast)

                if result.value != expected:
                    print(f"{WARNING}  Failed{ENDC}")
                    self.fail(
                        f"EXPRESSION:\n"
                        f"    {eval_input}\n"
                        f"EXPECTED RESULT= {expected}\n"
                        f"ACTUAL RESULT=  {result.value}\n"
                    )
            except ZeroDivisionError:
                continue
            except Exception as e:
                print(e, file=sys.stderr)
                assert False

        print(f"{SUCCESS}  Passed{ENDC}")

    def test_repl(self):
        self.print_header("REPL")
        try:
            proc = subprocess.run(
                ["python3", "nyaa.py"], capture_output=True, text=True, input="jaa ne"
            )

            if proc.returncode != 0:
                print(f"{ERROR}  Failed{ENDC}")
                self.fail(f"EXPECTED:\n    {proc.stderr}\nACTUAL:\n    {proc.stdout}")

            print(f"{SUCCESS}  Passed{ENDC}")
        except Exception as e:
            print(f"{ERROR}  Failed{ENDC}")
            print(e, file=sys.stderr)
            self.fail()


if __name__ == "__main__":
    unittest.main()
