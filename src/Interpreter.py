from src.utils.ErrorHandler import throw_unary_type_err, throw_not_implemented_err


class RunTimeValue:
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
        self.symbol_table = {}

    def interpret(self, ast):
        print("AST: ", ast, '\n')
        print(ast.accept(self))
        print()

    def visit(self, node):
        method = f"visit_{node.label}"
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_program(self, node: 'ProgramNode'):
        if node.eof:
            return

        # visit function definitions

        # visit body
        node.body.accept(self)

    def visit_func_def(self, node: 'FuncDefNode'):
        # print("visiting node: ", node)
        pass

    def visit_body(self, node: 'BodyNode'):
        res = []
        for stmt in node.statements:
            res.append(stmt.accept(self))
        return res

    def visit_print(self, node: 'PrintNode'):
        args = node.args.accept(self)
        for arg in args:
            print(arg)

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
                    return RunTimeValue("number", left.value + right.value)

                # String concatenation
                if left.label == "string" and right.label == "string":
                    return RunTimeValue("string", left.value + right.value)
            elif node.op == "-":
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("number", left.value - right.value)
            elif node.op == "*":
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("number", left.value * right.value)
            elif node.op == "/":
                if left.label == "number" and right.label == "number":
                    if right.value == 0:
                        raise ZeroDivisionError("Runtime error: Division by zero")
                    return RunTimeValue("number", left.value / right.value)
            elif node.op == 'and':
                if left.label == "boolean" and right.label == "boolean":
                    return RunTimeValue("boolean", left.value and right.value)
            elif node.op == 'or':
                if left.label == "boolean" and right.label == "boolean":
                    return RunTimeValue("boolean", left.value or right.value)
            elif node.op == '<':
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("boolean", left.value < right.value)
            elif node.op == '>':
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("boolean", left.value > right.value)
            elif node.op == '<=':
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("boolean", left.value <= right.value)
            elif node.op == '>=':
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("boolean", left.value >= right.value)
            elif node.op == '==':
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("boolean", left.value == right.value)

                if left.label == "string" and right.label == "string":
                    return RunTimeValue("boolean", left.value == right.value)
            elif node.op == '!=':
                if left.label == "number" and right.label == "number":
                    return RunTimeValue("boolean", left.value != right.value)

                if left.label == "string" and right.label == "string":
                    return RunTimeValue("boolean", left.value != right.value)
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

                return RunTimeValue("boolean", not right.value)
            elif left.value == '-':
                if right.label not in ["identifier", "number"]:
                    throw_unary_type_err(left.value, right.value)

                if right.label == "number":
                    return RunTimeValue("number", -right.value)

                # TODO: Implement negative operator for identifiers
                raise NotImplementedError("Negative operator not implemented for identifiers")
        return left

    @staticmethod
    def visit_operator(node: 'OperatorNode'):
        return RunTimeValue("operator", node.value)

    @staticmethod
    def visit_identifier(node: 'IdentifierNode'):
        return RunTimeValue("identifier", node.value)

    @staticmethod
    def visit_numeric_literal(node: 'NumericLiteralNode'):
        return RunTimeValue("number", node.value)

    @staticmethod
    def visit_string_literal(node: 'StringLiteralNode'):
        return RunTimeValue("string", node.value)

    @staticmethod
    def generic_visit(node):
        raise Exception(f'No visit_{node.label} method defined')
