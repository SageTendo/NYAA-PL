import sys

from src.core.AComponent import AComponent
from src.core.ASTNodes import PrintNode, BodyNode, ProgramNode, ArgsNode, ExprNode, SimpleExprNode, TermNode, \
    FactorNode, OperatorNode, IdentifierNode, NumericLiteralNode, StringLiteralNode, PassNode, InputNode, \
    AssignmentNode, PostfixExprNode, CallNode, FuncDefNode, ReturnNode, BooleanNode, IfNode, WhileNode
from src.core.RuntimeObject import RunTimeObject
from src.core.SymbolTable import SymbolTable
from src.utils.ErrorHandler import throw_unary_type_err, throw_invalid_operation_err, warning_msg, success_msg

MAX_VISIT_DEPTH = 5470
INTERNAL_RECURSION_LIMIT = 780
SYS_RECURSION_LIMIT = 1000000


class Interpreter(AComponent):
    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()

        # Safety nets
        self.__visitor_dept = 0
        self.func_call_count = 0
        self.conditional_flag = False
        sys.setrecursionlimit(SYS_RECURSION_LIMIT)

    def interpret(self, ast):
        """
        Interprets the given abstract syntax tree
        @param ast: The abstract syntax tree to interpret
        @return: The last runtime object returned by the program
        """
        try:
            return ast.accept(self)
        except RecursionError as e:
            print(
                "Visitor Error (´｡• ω •｡`):", e, file=sys.stderr)
            exit(1)

    def visit(self, node):
        """
        Gets the name of the visitor method and calls it on the node passed in as an argument
        @param node: The node to visit
        @return: The result of the visitor method
        """
        if self.__visitor_dept >= MAX_VISIT_DEPTH:
            # visitor depth exceeded and an error should be thrown
            # to prevent the Python interpreter from a segfault
            raise RecursionError(
                "Visitor depth exceeded! You've ventured too far into the code jungle. "
                "Time to retreat before you're lost in the wild recursion! (¬‿¬)")

        try:
            self.__visitor_dept += 1
            method = f"visit_{node.label}"

            self.debug(warning_msg(f"Visiting {node.label}"))
            visitor = getattr(self, method, self.generic_visit)(node)
            self.debug(success_msg(f"Returned --> {node.label}: {visitor}"))

            self.__visitor_dept -= 1
            return visitor
        except RecursionError as e:
            # Recursion depth exceeded by user defined functions
            print("Recursion Error:", e, file=sys.stderr)
            exit(1)
        except NotImplementedError as e:
            # visit method not implemented
            print("Visit Error:", e, file=sys.stderr)
            exit(1)
        except TypeError as e:
            print("Type Error: (╬ Ò﹏Ó)", e, file=sys.stderr)

    def handle_runtime_object(self, runtime_value: 'RunTimeObject'):
        if runtime_value.label == "identifier":
            return self.symbol_table.get_variable(runtime_value.value)
        else:
            return runtime_value.value

    def visit_program(self, node: 'ProgramNode'):
        if node.eof:
            return

        # visit function definitions
        for func in node.functions:
            func.accept(self)

        # visit body
        return node.body.accept(self)

    def visit_func_def(self, node: 'FuncDefNode'):
        """
        Visits a function definition
        @param node: The function definition node to visit
        """
        # Handle function parameters
        params = {}
        if node.args:
            for arg in node.args.accept(self):
                params[arg.value] = None

        # Add function and props to symbol table
        function_props = {'params': params, 'body': node.body}
        self.symbol_table.add_function_props(node.identifier, function_props)

    def visit_body(self, node: 'BodyNode'):
        # FIXME: Body nodes outside of conditional statements should not be visited if the condition is not met
        last_stmt = RunTimeObject('null', None)
        for stmt in node.statements:
            if stmt.label == 'return':
                return stmt.accept(self)
            last_stmt = stmt.accept(self)

            # conditional flag to break out of loop when condition is met
            if self.conditional_flag:
                break
        self.conditional_flag = False
        return last_stmt

    def visit_pass(self, node: 'PassNode'):
        node.accept(self)
        return RunTimeObject("null", None)

    def visit_return(self, node: 'ReturnNode'):
        if node.expr:
            return node.expr.accept(self)
        return RunTimeObject("null", None)

    def visit_if(self, node: 'IfNode'):
        expr = node.expr.accept(self)

        self.conditional_flag = True  # Set conditional flag when condition is met (expr is true)
        if expr.value and node.body:  # Handle if statement
            return node.body.accept(self)
        elif node.else_if_statements:  # Handle elif statements

            for else_if_stmt in node.else_if_statements:
                expr = else_if_stmt.expr.accept(self)

                if expr.value and else_if_stmt.body:
                    return else_if_stmt.body.accept(self)
        elif node.else_body:  # Handle else statement
            return node.else_body.accept(self)

        self.conditional_flag = False  # Reset conditional flag when not condition is met
        return RunTimeObject("null", None)

    def visit_while(self, node: 'WhileNode'):
        expr = node.expr.accept(self)

        while expr.value and node.body:
            node.body.accept(self)
            expr = node.expr.accept(self)
        return RunTimeObject('null', None)

    def visit_assignment(self, node: 'AssignmentNode'):
        """
        Visits an assignment statement
        @param node: The assignment node to visit
        """
        lhs = node.left.accept(self)
        rhs = node.right.accept(self)

        if rhs.label == "identifier":
            # Get variable and make a copy of its runtime object
            rhs = self.symbol_table.get_variable(rhs.value).copy()
        self.symbol_table.add_variable(lhs.value, rhs)
        return rhs

    def visit_call(self, node: 'CallNode'):
        """
        Visits a function call
        @param node: The function call node to visit
        """
        # Check for stack overflow
        self.func_call_count += 1
        if self.func_call_count > INTERNAL_RECURSION_LIMIT:
            self.func_call_count = 0
            raise RecursionError("Ara Ara! Interpreter recursion depth exceeded, "
                                 "that's not very kawaii of you... (◡﹏◡✿)")

        # Store current symbol table
        old_table = self.symbol_table

        # Get args for params
        identifier = node.identifier
        if node.args:
            args = node.args.accept(self)
            params = self.symbol_table.get_function_params(identifier)

            # Check for invalid number of args
            if len(args) != len(params):
                raise TypeError(
                    f"Invalid number of arguments provided, "
                    f"expected {len(params)} "
                    f"but got {len(args)}")

            # Store values of args
            arg_values = []
            for arg in args:
                if arg.label == "identifier":  # Get value from symbol table for variables
                    arg = self.symbol_table.get_variable(arg.value)
                arg_values.append(arg)

            # Create a local symbol table
            self.symbol_table = old_table.copy()

            # Assign args to params (setting local vars)
            for param in params:
                arg_runtime_value = arg_values.pop(0)
                self.symbol_table.add_variable(param, arg_runtime_value)

        # Visit function body
        result = self.symbol_table.get_function_body(identifier).accept(self)

        # Restore previous symbol table and func_call_count
        self.func_call_count -= 1
        self.symbol_table = old_table
        return result

    @staticmethod
    def visit_input(node: 'InputNode'):
        """
        Visits an input statement
        @param node: The input node to visit
        @return: The input value
        """
        value = input(node.message)
        return RunTimeObject('string', value)

    def visit_print(self, node: 'PrintNode'):
        args = node.args.accept(self)
        for arg in args:
            runtime_value = self.handle_runtime_object(arg)

            # Convert RunTimeObject to value if necessary
            # (Variable values are stored as RunTimeObjects)
            if isinstance(runtime_value, RunTimeObject):
                runtime_value = self.handle_runtime_object(runtime_value)
            print(runtime_value, end=' ')
        print()
        return RunTimeObject("null", None)

    def visit_postfix_expr(self, node: 'PostfixExprNode'):
        lhs = node.left.accept(self)

        # Variable value is stored as RunTimeObject
        runtime_object = self.handle_runtime_object(lhs)

        # Increment or decrement variable value
        if node.op == "++":
            runtime_object.value += 1
        elif node.op == '--':
            runtime_object.value -= 1
        return RunTimeObject("number", runtime_object.value)

    def visit_args(self, node: 'ArgsNode'):
        args = []
        for arg in node.children:
            args.append(arg.accept(self))
        return args

    def visit_expr(self, node: 'ExprNode'):
        expr = self.handle_expressions(node)
        return expr

    def visit_simple_expr(self, node: 'SimpleExprNode'):
        return self.handle_expressions(node)

    def visit_term(self, node: 'TermNode'):
        return self.handle_expressions(node)

    def handle_expressions(self, node):
        left = node.left.accept(self)
        if node.op:
            right = node.right.accept(self)

            # Get runtime object for left and right node, if they are identifier nodes
            if left.label == 'identifier':
                left = self.symbol_table.get_variable(left.value)
            if right.label == 'identifier':
                right = self.symbol_table.get_variable(right.value)

            # Handle operation
            if node.op in ["+", "-", 'or']:
                return self.handle_additive_expressions(left, right, node.op)
            elif node.op in ["*", "/", 'and']:
                return self.handle_multiplicative_expressions(left, right, node.op)
            elif node.op in ["==", "!=", "<", ">", "<=", ">="]:
                return self.handle_relational_expressions(left, right, node.op)

            # Invalid operation
            throw_invalid_operation_err(left.value, node.op, right.value)
        return left

    @staticmethod
    def handle_additive_expressions(left, right, op):
        if op == "+":

            if left.label == "string" and left.label == right.label:  # String concat
                return RunTimeObject("string", left.value + right.value)
            elif left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value + right.value)
        elif op == "-":

            if left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value - right.value)
        elif op == 'or':
            return RunTimeObject(left.label, left.value or right.value)

        # Invalid operation
        throw_invalid_operation_err(left.value, op, right.value)

    @staticmethod
    def handle_multiplicative_expressions(left, right, op):
        if op == "*":

            if ((left.label == "string" and right.label == "number")
                    or (left.label == "number" and right.label == "string")):
                return RunTimeObject("string", left.value * right.value)
            elif left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value * right.value)
        elif op == "/":

            if left.label == "number" and left.label == right.label:
                if right.value == 0:
                    raise ZeroDivisionError("Runtime error: Division by zero")
                return RunTimeObject("number", left.value / right.value)
        elif op == 'and':
            return RunTimeObject(right.label, left.value and right.value)

        # Invalid operation
        throw_invalid_operation_err(left.value, op, right.value)

    @staticmethod
    def handle_relational_expressions(left, right, op):
        if left.label == "string" and right.label == "number":

            res = eval(f"{len(left.value)} {op} {right.value}")
            return RunTimeObject("boolean", res)
        elif left.label == right.label:
            if left.label == "string":
                res = eval(f'"{left.value}" {op} "{right.value}"')
            else:
                res = eval(f"{left.value} {op} {right.value}")
            return RunTimeObject("boolean", res)

        # Invalid operation
        throw_invalid_operation_err(left.value, op, right.value)

    def visit_factor(self, node: 'FactorNode'):
        left = node.left.accept(self)

        if node.right:
            right = node.right.accept(self)

            # Check unary operator
            if left.value == 'not':
                if right.label not in ["string", "number", "identifier", "boolean"]:
                    throw_unary_type_err(left.value, right.value)

                return RunTimeObject("boolean", not right.value)
            elif left.value == '-':
                if right.label not in ["identifier", "number"]:
                    throw_unary_type_err(left.value, right.value)

                if right.label == "number":
                    return RunTimeObject("number", -right.value)
                else:
                    var_runtime_object = self.symbol_table.get_variable(right.value).copy()
                    if var_runtime_object.label != 'number':
                        raise TypeError("You gave me something that's not a number")
                    var_runtime_object.value *= -1
                    return var_runtime_object
        return left

    @staticmethod
    def visit_operator(node: 'OperatorNode'):
        return RunTimeObject("operator", node.value)

    @staticmethod
    def visit_identifier(node: 'IdentifierNode'):
        return RunTimeObject("identifier", node.value)

    @staticmethod
    def visit_numeric_literal(node: 'NumericLiteralNode'):
        return RunTimeObject("number", node.value)

    @staticmethod
    def visit_string_literal(node: 'StringLiteralNode'):
        return RunTimeObject("string", node.value)

    @staticmethod
    def visit_boolean_literal(node: 'BooleanNode'):
        return RunTimeObject("boolean", node.value)

    @staticmethod
    def generic_visit(node):
        raise NotImplementedError(f'No visit_{node.label} method defined')
