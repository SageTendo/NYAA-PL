import os.path
import subprocess

from src.Interpreter import Interpreter
from src.Lexer import Lexer
from src.Parser import Parser
from src.utils.Constants import WARNING, SUCCESS, ENDC, ERROR
from tests import BaseTest


class TestNyaa(BaseTest):
    def setUp(self):
        self.lexer: Lexer = Lexer()
        self.parser: Parser = Parser(lexer=self.lexer)
        self.interpreter: Interpreter = Interpreter()

    def test_interpreter(self):
        self.print_header("Interpreter")
        interpreter_dir = os.path.join(self.test_dir, "interpreter/")
        input_dir = os.path.join(interpreter_dir, "in/")
        output_dir = os.path.join(interpreter_dir, "out/")

        failed = False
        for file in os.listdir(input_dir):
            if not file.endswith(".ny"):
                continue

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
