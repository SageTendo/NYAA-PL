from src.AST.AST import PrintNode, BodyNode, ProgramNode, ArgsNode, ExprNode, SimpleExprNode, TermNode, \
    FactorNode, OperatorNode, IdentifierNode, NumericLiteralNode, StringLiteralNode, PassNode, InputNode, \
    AssignmentNode, PostfixExprNode, CallNode, FuncDefNode, ReturnNode
from src.SymbolTable import SymbolTable
from src.utils.ErrorHandler import throw_unary_type_err, throw_not_implemented_err


class RunTimeObject:
    def __init__(self, label, value, value_type=None):
        self.label = label
        self.value = value
        self.type = value_type

    def __repr__(self):
        if self.type is None:
            return f"{self.label.upper()}: {self.value}"
        return f"{self.label.upper()}: ({self.type}){self.value}"


class Interpreter:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.stack_pointer = 0

    def interpret(self, ast):
        ast.accept(self)
        print()

    def visit(self, node):
        method = f"visit_{node.label}"
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def handle_runtime_value(self, runtime_value: 'RunTimeObject'):
        if runtime_value.label == "identifier":
            return self.symbol_table.get_identifier(runtime_value.value)
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
        res = []
        for stmt in node.statements:
            res.append(stmt.accept(self))
        return res

    def visit_pass(self, node: 'PassNode'):
        pass

    def visit_return(self, node: 'ReturnNode'):
        if node.expr:
            return node.expr.accept(self)
        return RunTimeObject("null", None)

    def visit_assignment(self, node: 'AssignmentNode'):
        """
        Visits an assignment statement
        @param node: The assignment node to visit
        """
        lhs = node.left.accept(self)
        rhs = node.right.accept(self)
        self.symbol_table.add_identifier(lhs.value, rhs.value)

    def visit_call(self, node: 'CallNode'):
        """
        Visits a function call
        @param node: The function call node to visit
        """
        # Check for stack overflow
        if self.stack_pointer > 160:
            self.stack_pointer = 0
            raise RecursionError("Max recursion depth reached...")
        self.stack_pointer += 1

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
                arg_runtime_value = self.handle_runtime_value(arg)
                arg_values.append(arg_runtime_value)

            # Create a local symbol table
            self.symbol_table = old_table.copy()

            # Assign args to params (setting local vars)
            for param in params:
                arg_runtime_value = arg_values.pop(0)
                self.symbol_table.add_identifier(param, arg_runtime_value)

        # Visit function body
        result = self.symbol_table.get_function_body(identifier).accept(self).pop(0)

        # Restore previous symbol table and stack_pointer
        self.stack_pointer -= 1
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
            value = self.handle_runtime_value(arg)
            print(value, end=' ')
        print()

    def visit_postfix_expr(self, node: 'PostfixExprNode'):
        lhs = node.left.accept(self)
        curr_value = self.handle_runtime_value(lhs)

        if node.op == "++":
            self.symbol_table.set_identifier(lhs.value, curr_value + 1)
        elif node.op == '--':
            self.symbol_table.set_identifier(lhs.value, curr_value - 1)
        return RunTimeObject("number", self.symbol_table.get_identifier(lhs.value))

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

            if node.op == "+":
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("number", left.value + right.value)

                # String concatenation
                if left.label == "string" and right.label == "string":
                    return RunTimeObject("string", left.value + right.value)
            elif node.op == "-":
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("number", left.value - right.value)
            elif node.op == "*":
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("number", left.value * right.value)
            elif node.op == "/":
                if left.label == "number" and right.label == "number":
                    if right.value == 0:
                        raise ZeroDivisionError("Runtime error: Division by zero")
                    return RunTimeObject("number", left.value / right.value)
            elif node.op == 'and':
                if left.label == "boolean" and right.label == "boolean":
                    return RunTimeObject("boolean", left.value and right.value)
            elif node.op == 'or':
                if left.label == "boolean" and right.label == "boolean":
                    return RunTimeObject("boolean", left.value or right.value)
            elif node.op == '<':
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("boolean", left.value < right.value)
            elif node.op == '>':
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("boolean", left.value > right.value)
            elif node.op == '<=':
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("boolean", left.value <= right.value)
            elif node.op == '>=':
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("boolean", left.value >= right.value)
            elif node.op == '==':
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("boolean", left.value == right.value)

                if left.label == "string" and right.label == "string":
                    return RunTimeObject("boolean", left.value == right.value)
            elif node.op == '!=':
                if left.label == "number" and right.label == "number":
                    return RunTimeObject("boolean", left.value != right.value)

                if left.label == "string" and right.label == "string":
                    return RunTimeObject("boolean", left.value != right.value)
            throw_not_implemented_err(f"Expr: {left.value} {node.op} {right.value}", -1, -1)
        return left

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

                # TODO: Implement negative operator for identifiers
                raise NotImplementedError("Negative operator not implemented for identifiers")
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
    def generic_visit(node):
        raise Exception(f'No visit_{node.label} method defined')
