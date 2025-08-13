import subprocess
import sys
import unittest

from src.utils.Constants import SUCCESS, ENDC, ERROR
from tests import BaseTest


class TestRepl(BaseTest):
    def setUp(self): ...

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
