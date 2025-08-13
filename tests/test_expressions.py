import os.path
import sys
from random import randint, choice

from src.Interpreter import Interpreter
from src.Lexer import Lexer
from src.Parser import Parser
from src.utils.Constants import WARNING, SUCCESS, ENDC, ERROR
from tests import BaseTest


class TestExpressions(BaseTest):
    test_dir = os.path.dirname(__file__)

    def setUp(self):
        self.lexer: Lexer = Lexer()
        self.parser: Parser = Parser(lexer=self.lexer)
        self.interpreter: Interpreter = Interpreter()
        self.num_random_tests = 15000

    def test_operator_precedence_expressions(self):
        self.print_header("Operator Precedence Expressions")
        operators = [
            "+",
            "-",
            "*",
            "/",
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
            test_input = f"{a} {op1} {b} {op2} {c} {op3} {d} {op1} {e} {op2} {f}"
            try:
                expected = eval(test_input)
                ast = self.parser.parse_repl(repl_input=test_input)
                result = self.interpreter.interpret(ast)

                if result.value != expected:
                    print(f"{ERROR}   Failed{ENDC}")
                    self.fail(
                        f"EXPRESSION:\n"
                        f"    {test_input}\n"
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
            "+",
            "-",
            "*",
            "/",
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
            test_input = f"({a} {op1} {b}) {op2} ({c} {op3} {d})"

            try:
                expected = eval(test_input)
                ast = self.parser.parse_repl(repl_input=test_input)
                result = self.interpreter.interpret(ast)

                if result.value != expected:
                    print(f"{WARNING}  Failed{ENDC}")
                    self.fail(
                        f"EXPRESSION:\n"
                        f"    {test_input}\n"
                        f"EXPECTED RESULT= {expected}\n"
                        f"ACTUAL RESULT=  {result.value}\n"
                    )
            except ZeroDivisionError:
                continue
            except Exception as e:
                print(e, file=sys.stderr)
                assert False

        print(f"{SUCCESS}  Passed{ENDC}")
