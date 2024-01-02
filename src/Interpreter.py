import sys

from src.core.AComponent import AComponent
from src.core.ASTNodes import PrintNode, BodyNode, ProgramNode, ArgsNode, ExprNode, SimpleExprNode, TermNode, \
    FactorNode, OperatorNode, IdentifierNode, NumericLiteralNode, StringLiteralNode, PassNode, InputNode, \
    AssignmentNode, PostfixExprNode, CallNode, FuncDefNode, ReturnNode, BooleanNode, IfNode, WhileNode, BreakNode, \
    ContinueNode
from src.core.Environment import Environment
from src.core.CacheMemory import cache_mem
from src.core.RuntimeObject import RunTimeObject
from src.utils.Constants import WARNING
from src.utils.ErrorHandler import throw_unary_type_err, throw_invalid_operation_err, warning_msg, success_msg, emoji, \
    InterpreterError, ErrorType

MAX_VISIT_DEPTH = 5470
INTERNAL_RECURSION_LIMIT = 1010
SYS_RECURSION_LIMIT = 1000000


class Interpreter(AComponent):
    def __init__(self):
        super().__init__()
        self.global_env = Environment(name="global", level=1)
        self.current_env = self.global_env

        #  Control flow flags
        self.conditional_flag = False
        self.break_flag = False
        self.continue_flag = False

        # Safety nets
        self.__visitor_depth = 0  # Keep track of the depth of the visitor
        self.__internal_recursion_depth = 0  # Keep track of number of recursive function calls
        sys.setrecursionlimit(SYS_RECURSION_LIMIT)

        # Error handling
        self.node_start_pos = (-1, -1)
        self.node_end_pos = (-1, -1)

    def interpret(self, ast):
        """
        Interprets the given abstract syntax tree
        @param ast: The abstract syntax tree to interpret
        @return: The last runtime object returned by the program
        """
        try:
            return ast.accept(self)
        except RecursionError as e:
            print(f"{emoji()}\n"
                  f"Visitor Error:", e, file=sys.stderr)
        except InterpreterError as e:
            print(e, file=sys.stderr)

    def visit(self, node):
        """
        Gets the name of the visitor method and calls it on the node passed in as an argument
        @param node: The node to visit
        @return: The result of the visitor method
        """
        if self.__visitor_depth >= MAX_VISIT_DEPTH:
            # visitor depth exceeded and an error should be thrown
            # to prevent the Python interpreter from a segfault
            raise RecursionError(
                "Visitor depth exceeded! You've ventured too far into the code jungle. "
                "Time to retreat before you're lost in the wild recursion! (¬‿¬)")

        self.__visitor_depth += 1
        method = f"visit_{node.label}"

        self.debug(warning_msg(f"Visiting {node.label}"))
        visit_method = getattr(self, method, self.generic_visit)

        # Cache node visits
        if not cache_mem.has_key(node):
            cache_mem.put(node, visit_method)

        # Visit (in the case of cache misses)
        if result := visit_method(node):
            self.debug(success_msg(f"Returned --> {node.label}: {result}"))

        self.__visitor_depth -= 1
        return result

    def __get_runtime_value(self, runtime_obj: 'RunTimeObject'):
        """
        Returns the runtime value of a runtime object
        @param runtime_obj: The object to return the value from
        @return: The runtime value of the runtime object
        """
        runtime_obj = self.__test_for_identifier(runtime_obj)
        return runtime_obj.value

    def __test_for_identifier(self, runtime_object: 'RunTimeObject', current_scope=False):
        """
        Checks if the runtime object is an identifier, and returns
        the value held by the identifier
        @param runtime_object: The runtime object to test
        @return: The non-identifier runtime object
        """
        if runtime_object.label == "identifier":
            return self.current_env.lookup_variable(runtime_object.value, current_scope=current_scope)
        else:
            return runtime_object

    def visit_program(self, node: 'ProgramNode'):
        """
        Interprets a program node and returns the result of the program execution
        @param node: The program node to visit
        @return: The result of the program execution
        """
        if node.eof:
            return

        for func in node.functions:
            func.accept(self)

        # visit body
        node.body.accept(self)
        self.current_env = None

    def visit_func_def(self, node: 'FuncDefNode'):
        """
        Interprets a function definition node and add the function
        and its properties to the symbol table
        @param node: The function definition node to visit
        """
        params = {}
        if node.args:
            for arg in node.args.accept(self):
                if arg.value in params:
                    raise InterpreterError(ErrorType.RUNTIME,
                                           f"Duplicate parameter {WARNING}'{arg.value}'",
                                           node.args.start_pos, node.args.end_pos)
                params[arg.value] = arg.type
        self.current_env.insert_function(node.identifier, params, node.body)

    def visit_body(self, node: 'BodyNode'):
        """
        Visits a body node and interprets the statements in the body
        and returns the result of the last evaluated statement
        @param node: The body node to visit
        @return: The result of the last evaluated statement
        """
        last_evaluated = None

        for stmt in node.statements:
            if stmt.label == "break":
                # Set break flag and continue
                self.break_flag = True
                break
            elif stmt.label == "continue":
                self.continue_flag = True
                continue
            elif stmt.label == "pass":
                continue

            # Check if condition flags is set and if so, stop visiting the body and return
            if self.conditional_flag:
                break

            evaluated = stmt.accept(self)
            last_evaluated = evaluated if evaluated else last_evaluated
            if stmt.label == "return":
                return last_evaluated

        self.conditional_flag = False  # Reset condition flag
        return last_evaluated

    def visit_pass(self, node: 'PassNode'):
        pass

    def visit_break(self, node: 'BreakNode'):
        pass

    def visit_continue(self, node: 'ContinueNode'):
        pass

    def visit_return(self, node: 'ReturnNode'):
        """
        Interprets a return node and returns the result of the expression if any
        @param node: The return node to visit
        @return: The result of the expression if any
        """
        if node.expr:
            return node.expr.accept(self)

    def __handle_conditional_execution(self, body_node: 'BodyNode'):
        """
        Handles the execution of a conditional body node
        and returns the result of the last evaluated statement if any
        @param body_node: The body node to visit
        @return: The result of the last evaluated statement if anything is returned
        """
        if not body_node:  # Empty body
            return

        stmt = body_node.accept(self)
        last_node = body_node.statements[-1]
        if last_node.label == "return":
            self.conditional_flag = True
            return stmt
        elif last_node.label in ["continue", "break"]:
            self.conditional_flag = True

    def visit_if(self, node: 'IfNode'):
        """
        Visits an if node and interprets its body if the specified condition is true,
        and returns the result of the last evaluated statement if any
        @param node: The if statement node to visit
        @return: The result of the last evaluated statement if any
        """
        expr = node.expr.accept(self)
        body = node.body

        if expr.value:
            # Handle if statement
            if stmt := self.__handle_conditional_execution(body):
                return stmt

        elif node.else_if_statements:
            for else_if_stmt in node.else_if_statements:
                # Handle elif statement
                expr = else_if_stmt.expr.accept(self)
                if not expr.value:
                    continue

                if stmt := self.__handle_conditional_execution(else_if_stmt.body):
                    return stmt
        elif node.else_body:
            # Handle else statement
            if stmt := self.__handle_conditional_execution(node.else_body):
                return stmt

    def visit_while(self, node: 'WhileNode'):
        """
        Visits a while node and interprets its body while the condition is true,
        and returns the result of the last evaluated statement if any
        @param node: The while statement node to visit
        @return: The result of the last evaluated statement if any
        """
        expr = node.expr.accept(self)

        while expr.value and node.body:
            # Handle while body
            if stmt := self.__handle_conditional_execution(node.body):
                return stmt

            # Handle control flow statements
            if self.continue_flag:
                self.continue_flag = False
                continue
            elif self.break_flag:
                self.break_flag = False
                break

            # Evaluate condition
            expr = node.expr.accept(self)

    def visit_assignment(self, node: 'AssignmentNode'):
        """
        Visits an assignment statement and handles the assignment operation of identifiers
        @param node: The assignment node to visit
        """
        lhs = node.left.accept(self)
        rhs = node.right.accept(self)

        rhs = self.__test_for_identifier(rhs, current_scope=True)
        self.current_env.insert_variable(lhs.value,
                                         RunTimeObject(label=rhs.label, value=rhs.value, value_type=rhs.type))
        return rhs

    def visit_call(self, node: 'CallNode'):
        """
        Visits a function call and gets the function's parameters and body,
        and then interprets the function
        @param node: The function call node to visit
        """
        # Check for stack overflow
        self.__internal_recursion_depth += 1
        if self.__internal_recursion_depth > INTERNAL_RECURSION_LIMIT:
            self.__internal_recursion_depth = 0
            raise InterpreterError(ErrorType.RECURSION, "Ara Ara!!!\nNon-kawaii recursion depth exceeded",
                                   node.start_pos, node.end_pos)

        #  Create a local scope for the current function call and keep reference of the previous scope
        local_env = Environment(name=node.identifier,
                                level=self.current_env.level + 1,
                                parent=self.global_env
                                )
        old_env = self.current_env

        # Get the function symbol from the symbol table
        function_symbol = self.current_env.lookup_function(node.identifier)
        if node.args:
            args = node.args.accept(self)

            # Check for invalid number of args
            if len(args) != len(function_symbol.params):
                raise InterpreterError(ErrorType.RUNTIME,
                                       f"Invalid number of arguments provided...\n"
                                       f"Expected {len(function_symbol.params)} "
                                       f"but got {len(args)}", node.args.start_pos, node.args.end_pos)

            # Assign args to params (setting local vars)
            for i, param in enumerate(function_symbol.params):
                arg_runtime_object = self.__test_for_identifier(args[i])
                local_env.insert_variable(param, arg_runtime_object)
        self.current_env = local_env

        # Check cache for previously stored value, else walk through the function body
        env_hash = hash(self.current_env)
        if result := cache_mem.get(env_hash):
            result = self.__test_for_identifier(result)
        elif result := function_symbol.body.accept(self):
            result = self.__test_for_identifier(result)
            cache_mem.put(env_hash, result)

        # Restore previous environment and internal recursion depth
        self.current_env = old_env
        self.__internal_recursion_depth -= 1
        return result

    @staticmethod
    def visit_input(node: 'InputNode'):
        """
        Gets input from the user and returns it when an input node is visited
        @param node: The input node being visited
        @return: The value inputted by the user
        """
        value = input(node.message)
        return RunTimeObject('string', value)

    def visit_print(self, node: 'PrintNode'):
        """
        Visits a print statement node and prints the value(s) of evaluated argument(s) to the console
        @param node: The print statement node to visit
        """
        args = node.args.accept(self)
        for arg in args:
            runtime_value = self.__get_runtime_value(arg)
            print(runtime_value, end=' ')
        print()

    def visit_postfix_expr(self, node: 'PostfixExprNode'):
        """
        Visits a postfix expression node and returns the result of the expression evaluated
        @param node: The postfix expression node to visit
        @return: The result of the postfix expression
        """
        lhs = node.left.accept(self)

        # Variable value is stored as RunTimeObject
        runtime_object = self.__test_for_identifier(lhs)
        if node.op == "++":
            runtime_object.value += 1
        elif node.op == '--':
            runtime_object.value -= 1
        return RunTimeObject("number", runtime_object.value)

    def visit_args(self, node: 'ArgsNode'):
        """
        Visits the arguments node and returns the a list of values
        associated with the evaluated arguments
        @param node: The arguments node to visit
        @return:  List of argument values evaluated
        """
        args = []
        for arg in node.children:
            args.append(arg.accept(self))
        return args

    def visit_expr(self, node: 'ExprNode'):
        """
        Visits an expression node and returns the result of the evaluated expression
        @param node: The expression node to visit
        @return: The result of the expression evaluated
        """
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos

        expr = self.handle_expressions(node)
        return expr

    def visit_simple_expr(self, node: 'SimpleExprNode'):
        """
        Visits a simple expression node and returns the result of the evaluated expression
        @param node: The simple expression node to visit
        @return: The result of the expression evaluated
        """
        return self.handle_expressions(node)

    def visit_term(self, node: 'TermNode'):
        """
        Visits a term node and returns the result of the evaluated expression
        @param node: The term node to visit
        @return: The result of the expression evaluated
        """
        return self.handle_expressions(node)

    def handle_expressions(self, node):
        """
        Handles expressions and returns the result of the operation
        associated with the expression
        @param node: The expression node to handle
        @return: The result of the operation
        """
        left = node.left.accept(self)
        if node.op:
            right = node.right.accept(self)

            # Get runtime object for left and right node, if they are identifier nodes
            left = self.__test_for_identifier(left)
            right = self.__test_for_identifier(right)

            # Handle operation
            if node.op in ["+", "-", 'or']:
                return self.handle_additive_expressions(left, right, node.op)
            elif node.op in ["*", "/", 'and']:
                return self.handle_multiplicative_expressions(left, right, node.op)
            elif node.op in ["==", "!=", "<", ">", "<=", ">="]:
                return self.handle_relational_expressions(left, right, node.op)

            # Invalid operation
            throw_invalid_operation_err(left.label, node.op, right.label,
                                        self.node_start_pos, self.node_end_pos)
        return left

    def handle_additive_expressions(self, left, right, op):
        """
        Handles additive expressions and returns the result of the operation
        @param left: The left operand of the operation
        @param right: The right operand of the operation
        @param op: The operation to perform
        @return: The result of the operation
        """
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
        throw_invalid_operation_err(left.label, op, right.label,
                                    self.node_start_pos, self.node_end_pos)

    def handle_multiplicative_expressions(self, left, right, op):
        """
        Handles multiplicative expressions and returns the result of the operation
        as a runtime object
        @param left: The left operand of the operation
        @param right: The right operand of the operation
        @param op: The operation to perform
        @return: The result of the operation
        """
        if op == "*":

            if ((left.label == "string" and right.label == "number")
                    or (left.label == "number" and right.label == "string")):
                return RunTimeObject("string", left.value * right.value)
            elif left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value * right.value)
        elif op == "/":

            if left.label == "number" and left.label == right.label:
                if right.value == 0:
                    raise InterpreterError(ErrorType.RUNTIME,
                                           "Division by zero is not kawaii, please don't do that.",
                                           self.node_start_pos, self.node_end_pos)
                return RunTimeObject("number", left.value / right.value)
        elif op == 'and':
            return RunTimeObject(right.label, left.value and right.value)

        # Invalid operation
        throw_invalid_operation_err(left.label, op, right.label,
                                    self.node_start_pos, self.node_end_pos)

    def handle_relational_expressions(self, left, right, op):
        """
        Handles relational expressions and returns the result of the operation
        as a runtime object
        @param left: The left operand of the operation
        @param right: The right operand of the operation
        @param op: The operation to perform
        @return: The result of the operation
        """
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
        throw_invalid_operation_err(left.label, op, right.label,
                                    self.node_start_pos, self.node_end_pos)

    def visit_factor(self, node: 'FactorNode'):
        """
        Visits a factor node and returns the result of the evaluated factor
        @param node: The factor node to visit
        @return: The result of the factor evaluated
        """
        left = node.left.accept(self)

        if node.right:
            right = node.right.accept(self)

            # Check unary operator
            if left.value == 'not':
                if right.label not in ["string", "number", "identifier", "boolean"]:
                    throw_unary_type_err(left.value, right.value,
                                         self.node_start_pos, self.node_end_pos)

                return RunTimeObject("boolean", not right.value)
            elif left.value == '-':
                if right.label not in ["identifier", "number"]:
                    throw_unary_type_err(left.value, right.label,
                                         self.node_start_pos, self.node_end_pos)

                if right.label == "number":
                    return RunTimeObject("number", -right.value)
                else:
                    var_runtime_object = self.current_env.lookup_variable(right.value).copy()
                    if var_runtime_object.label != 'number':
                        raise InterpreterError(ErrorType.TYPE,
                                               "You gave me something that's not a number",
                                               self.node_start_pos, self.node_end_pos)

                    # Negate the value
                    var_runtime_object.value *= -1
                    return var_runtime_object
        return left

    @staticmethod
    def visit_operator(node: 'OperatorNode'):
        """
        Visits an operator and returns the value as a runtime object
        @param node: The operator node to visit
        @return: The operator value as a runtime object
        """
        return RunTimeObject("operator", node.value)

    @staticmethod
    def visit_identifier(node: 'IdentifierNode'):
        """
        Visits an identifier and returns the value as a runtime object
        @param node: The identifier node to visit
        @return: The identifier value as a runtime object
        """
        return RunTimeObject("identifier", node.value)

    @staticmethod
    def visit_numeric_literal(node: 'NumericLiteralNode'):
        """
        Visits a numeric literal and returns the value as a runtime object
        @param node: The numeric literal node to visit
        @return: The numeric literal value as a runtime object
        """
        return RunTimeObject("number", node.value)

    @staticmethod
    def visit_string_literal(node: 'StringLiteralNode'):
        """
        Visits a string literal and returns the value as a runtime object
        @param node: The string literal node to visit
        @return: The string literal value as a runtime object
        """
        return RunTimeObject("string", node.value)

    @staticmethod
    def visit_boolean_literal(node: 'BooleanNode'):
        """
        Visits a boolean literal and returns the value as a runtime object
        @param node: The boolean literal node to visit
        @return: The boolean literal value as a runtime object
        """
        return RunTimeObject("boolean", node.value)

    @staticmethod
    def generic_visit(node):
        """
        Called if no visitor function exists for a node.
        @param node: The node to visit
        """
        raise NotImplementedError(f'No visit_{node.label} method defined')
