import sys

from src.core.ASTNodes import (
    PrintNode,
    BodyNode,
    ProgramNode,
    ArgsNode,
    ExprNode,
    SimpleExprNode,
    TermNode,
    FactorNode,
    OperatorNode,
    IdentifierNode,
    NumericLiteralNode,
    StringLiteralNode,
    InputNode,
    AssignmentNode,
    PostfixExprNode,
    CallNode,
    FuncDefNode,
    ReturnNode,
    BooleanNode,
    IfNode,
    WhileNode,
    ForNode,
    BreakNode,
    ContinueNode,
    ArrayNode,
)
from src.core.CacheMemory import cache_mem
from src.core.Environment import Environment
from src.core.RuntimeObject import RunTimeObject
from src.core.Symbol import ArraySymbol
from src.utils.Constants import WARNING
from src.utils.ErrorHandler import (
    throw_unary_type_err,
    throw_invalid_operation_err,
    warning_msg,
    success_msg,
    emoji,
    InterpreterError,
    ErrorType,
)

MAX_VISIT_DEPTH = 5470
INTERNAL_RECURSION_LIMIT = 1010
SYS_RECURSION_LIMIT = 1000000


class Interpreter:
    def __init__(self, verbose: bool = False):
        self.__verbose = verbose
        self.global_env: Environment = Environment(name="global", level=1)
        self.current_env = self.global_env

        #  Control flow flags
        self.conditional_flag = False
        self.break_flag = False
        self.continue_flag = False

        # Safety nets
        self.__visitor_depth = 0  # Keep track of the depth of the visitor
        self.__recursion_count = 0  # Keep track of number of recursive function calls
        sys.setrecursionlimit(SYS_RECURSION_LIMIT)

        # Error handling
        self.node_start_pos = (-1, -1)
        self.node_end_pos = (-1, -1)

    def __log(self, message: str):
        if self.__verbose:
            print(message)

    def interpret(self, ast):
        """
        Interprets the given abstract syntax tree
        @param ast: The abstract syntax tree to interpret
        @return: The last runtime object returned by the program
        """
        try:
            return ast.accept(self)
        except RecursionError as e:
            print(f"{emoji()}\n" f"Visitor Error:", e, file=sys.stderr)
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
                "Time to retreat before you're lost in the wild recursion! (¬‿¬)"
            )

        if self.current_env is None:
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Undefined scope. Please define a scope before executing statements",
                node.start_pos,
                node.end_pos,
            )

        self.__visitor_depth += 1
        method = f"visit_{node.label}"
        self.__log(warning_msg(f"Visiting {node.label}"))
        visit_method = getattr(self, method, self.generic_visit)

        # Cache node visit
        if not cache_mem.has_key(node):
            cache_mem.put(node, visit_method)

        # Visit (in the case of cache misses)
        if result := visit_method(node):
            self.__log(success_msg(f"Returned --> {node.label}: {result}"))

        self.__visitor_depth -= 1
        return result

    def visit_program(self, node: ProgramNode):
        """
        Interprets a program node and returns the result of the program execution
        @param node: The program node to visit
        @return: The result of the program execution
        """
        if node.eof:
            return

        for func in node.functions:
            func.accept(self)

        node.body.accept(self)
        self.current_env = None

    def visit_func_def(self, node: "FuncDefNode"):
        """
        Interprets a function definition node and add the function
        and its properties to the symbol table
        @param node: The function definition node to visit
        """
        params = {}
        if node.args:
            for arg in node.args.accept(self):
                if arg.value not in params:
                    params[arg.value] = arg.type
                else:
                    raise InterpreterError(
                        ErrorType.RUNTIME,
                        f"Duplicate parameter {WARNING}'{arg.value}'",
                        node.args.start_pos,
                        node.args.end_pos,
                    )
        self.current_env.insert_function(node.identifier, params, node.body)  # type: ignore

    def visit_body(self, node: "BodyNode"):
        """
        Visits a body node and interprets the statements in the body
        and returns the result of the last evaluated statement
        @param node: The body node to visit
        @return: The result of the last evaluated statement
        """
        last_evaluated_stmt = None
        for stmt in node.statements:

            if self.conditional_flag:
                self.conditional_flag = False
                break

            elif self.break_flag:
                break

            elif self.continue_flag:
                self.continue_flag = False
                continue

            evaluated_stmt = stmt.accept(self)
            last_evaluated_stmt = (
                evaluated_stmt if evaluated_stmt is not None else last_evaluated_stmt
            )
            if stmt.label == "return":
                return last_evaluated_stmt
        return last_evaluated_stmt

    def visit_return(self, node: "ReturnNode"):
        """
        Interprets a return node and returns the result of the expression if any
        @param node: The return node to visit
        @return: The result of the expression if any
        """
        if node.expr is not None:
            return node.expr.accept(self)

    def visit_break(self, node: "BreakNode"):
        """Interprets a break node"""
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        self.break_flag = True

    def visit_continue(self, node: "ContinueNode"):
        """Interprets a continue node"""
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        self.continue_flag = True

    def __handle_conditional_execution(self, body_node: "BodyNode"):
        """
        Handles the execution of a conditional body node
        and returns the result of the last evaluated statement if any
        @param body_node: The body node to visit
        @return: The result of the last evaluated statement if anything is returned
        """
        if body_node is None:
            return

        last_evaluated_stmt = body_node.accept(self)
        last_node = body_node.statements[-1]
        if last_node.label == "return":
            self.conditional_flag = True
            return last_evaluated_stmt

    def visit_if(self, node: "IfNode"):
        """
        Visits an if node and interprets its body if the specified condition is true,
        and returns the result of the last evaluated statement if any
        @param node: The if statement node to visit
        @return: The result of the last evaluated statement if any
        """
        condition = node.expr.accept(self)
        if condition.value:
            return self.__handle_conditional_execution(node.body)

        for else_if_stmt in node.else_if_statements:
            condition = else_if_stmt.expr.accept(self)
            if condition.value:
                return self.__handle_conditional_execution(else_if_stmt.body)

        if node.else_body is not None:
            return self.__handle_conditional_execution(node.else_body)

    def visit_while(self, node: "WhileNode"):
        """
        Visits a while node and interprets its body while the condition is true,
        and returns the result of the last evaluated statement if any
        @param node: The while statement node to visit
        @return: The result of the last evaluated statement if any
        """
        condition = node.expr.accept(self)
        while condition.value:
            if stmt := self.__handle_conditional_execution(node.body):
                return stmt

            if self.break_flag:
                self.break_flag = False
                break

            condition = node.expr.accept(self)  # Re-evaluate condition

    def visit_for(self, node: "ForNode"):
        """
        Visits a for loop and creates an iterator in the symbol table and interprets its body for the specified range
        @param node: The for loop node to visit
        @return: The result of the last evaluated statement if any
        @raise InterpreterError: If the range value is not an integer
        """

        def validate_range_node(range_node):
            """
            Validate a range node.
            @param range_node: The range node to validate.
            @return int: The validated range value.
            @raise InterpreterError: If the range value is not an integer.
            """
            runtime_object = range_node.accept(self)
            if type(runtime_object.value) is not int:
                raise InterpreterError(
                    ErrorType.RUNTIME,
                    f"Range value '{type(runtime_object.value).__name__}' "
                    f"cannot be used as an integer",
                    range_node.start_pos,
                    range_node.end_pos,
                )
            return runtime_object.value

        range_start = validate_range_node(node.range_start)
        range_end = validate_range_node(node.range_end)

        # Create iterator in symbol table
        iterator_runtime_object = RunTimeObject(
            label="number", value=0, value_type="int"
        )
        self.current_env.insert_variable(node.identifier.value, iterator_runtime_object)  # type: ignore

        # incrementer to determine direction of iteration
        incrementer = 1 if range_start < range_end else -1
        for i in range(range_start, range_end, incrementer):
            iterator_runtime_object.value = i
            if last_evaluated := self.__handle_conditional_execution(node.body):
                return last_evaluated

    def visit_array_def(self, node: "ArrayNode"):
        """
        Visits an ArrayNode and creates a new array in the symbol table
        @param node: The ArrayNode to visit
        """
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos

        identifier = node.identifier
        if node.size is not None:
            array_size = self.__test_for_identifier(node.size.accept(self)).value
            values = [RunTimeObject("null", value="null")] * int(array_size)

        elif node.initial_values is not None:
            array_size = len(node.initial_values)
            values = [value.accept(self) for value in node.initial_values]

        else:
            array_size = -1
            values = []

        array_symbol = ArraySymbol(identifier, array_size, values)
        self.current_env.insert_array(identifier, array_symbol)  # type: ignore

    def visit_array_access(self, node: "ArrayNode"):
        """
        Visits an ArrayNode and returns an element of the array in the symbol table
        @param node: The ArrayNode to visit
        """
        identifier = node.identifier
        index = self.__test_for_identifier(node.index.accept(self)).value
        array_symbol = self.current_env.lookup_array(identifier)  # type: ignore

        if index < 0 or index >= len(array_symbol.values):
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Array index out of bounds",
                node.start_pos,
                node.end_pos,
            )

        return array_symbol.values[index]

    def visit_array_update(self, node: "ArrayNode"):
        """
        Visits an ArrayNode and updates the array in the symbol table
        @param node: The ArrayNode to visit
        """
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos

        identifier = node.identifier
        index = self.__test_for_identifier(node.index.accept(self)).value  # type: ignore
        value_runtime = node.value.accept(self)

        array_symbol = self.current_env.lookup_array(identifier)  # type: ignore
        if int(index) < 0 or int(index) >= len(array_symbol.values):
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Array index out of bounds",
                node.start_pos,
                node.end_pos,
            )

        array_symbol.values[index] = RunTimeObject(
            value_runtime.label, value_runtime.value, value_runtime.type
        )

    def visit_assignment(self, node: "AssignmentNode"):
        """
        Visits an assignment statement and handles the assignment operation of identifiers
        @param node: The assignment node to visit
        """
        lhs = node.left.accept(self)
        rhs = node.right.accept(self)
        self.current_env.insert_variable(lhs.value, RunTimeObject(rhs.label, rhs.value, rhs.type))  # type: ignore

    def visit_call(self, node: "CallNode"):
        """
        Visits a function CallNode, fetches the function symbol from the symbol table,
        creates a new environment for the function call and handles its execution.
        @param node: The CallNode being visited
        """
        self.check_for_stack_overflow(node)

        local_env = Environment(
            name=node.identifier,
            level=self.current_env.level + 1,  # type: ignore
            parent=self.global_env,
        )
        old_env = self.current_env
        function_symbol = self.current_env.lookup_function(node.identifier)  # type: ignore

        if node.args is not None:
            function_args = node.args.accept(self)
            if len(function_args) != len(function_symbol.params):
                raise InterpreterError(
                    ErrorType.RUNTIME,
                    f"Invalid number of arguments provided...\n"
                    f"Expected {len(function_symbol.params)} "
                    f"but got {len(function_args)}",
                    node.args.start_pos,
                    node.args.end_pos,
                )

            # assing arg values to local variables
            for i, param in enumerate(function_symbol.params):
                local_env.insert_variable(param, function_args[i])

        self.current_env = local_env

        # Check cache for previously stored value, else walk through the function body
        env_hash = self.current_env.hash()
        result = cache_mem.get(env_hash)
        if result is None:
            result = function_symbol.body.accept(self)
            cache_mem.put(env_hash, result)

        self.current_env = old_env
        self.__recursion_count -= 1
        return result

    @staticmethod
    def visit_input(node: "InputNode"):
        """
        Gets input from the user and returns it when an input node is visited
        @param node: The input node being visited
        @return: The value inputted by the user
        """
        value = input(node.message)
        return RunTimeObject("string", value)

    def visit_print(self, node: "PrintNode"):
        """
        Visits a print statement node and prints the value(s) of evaluated argument(s) to the console
        @param node: The print statement node to visit
        """
        args = node.args.accept(self)
        for i, arg in enumerate(args):
            runtime_value = arg.value
            if i < len(args) - 1:
                print(runtime_value, end=" ")
            else:
                print(runtime_value, end="")

        if node.println:  # print new line if println is used
            print()

    def visit_postfix_expr(self, node: "PostfixExprNode"):
        """
        Visits a postfix expression node and returns the result of the expression evaluated
        @param node: The postfix expression node to visit
        @return: The result of the postfix expression
        """
        lhs = node.left.accept(self)

        runtime_object = self.__test_for_identifier(lhs)
        runtime_object.value += 1 if node.operator == "++" else -1
        return RunTimeObject("number", runtime_object.value)

    def visit_args(self, node: "ArgsNode"):
        """
        Visits the arguments node and returns the a list of values
        associated with the evaluated arguments
        @param node: The arguments node to visit
        @return:  List of argument values evaluated
        """
        return [arg_node.accept(self) for arg_node in node.children]

    def visit_expr(self, node: "ExprNode"):
        """
        Visits an expression node and returns the result of the evaluated expression
        @param node: The expression node to visit
        @return: The result of the expression evaluated
        """
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        return self.handle_expressions(node)

    def visit_simple_expr(self, node: "SimpleExprNode"):
        """
        Visits a simple expression node and returns the result of the evaluated expression
        @param node: The simple expression node to visit
        @return: The result of the expression evaluated
        """
        return self.handle_expressions(node)

    def visit_term(self, node: "TermNode"):
        """
        Visits a term node and returns the result of the evaluated expression
        @param node: The term node to visit
        @return: The result of the expression evaluated
        """
        return self.handle_expressions(node)

    def handle_expressions(self, node):
        """
        Handles expressions and returns a runtime object representing the result of the operation
        @param node: The expression node to handle
        @return: A RunTimeObject representing the result of the operation
        """
        left = node.left.accept(self)
        left = self.__test_for_identifier(left)

        if node.operator is not None:
            right = node.right.accept(self)
            right = self.__test_for_identifier(right)

            # Handle operation
            if node.operator in ["+", "-", "or"]:
                return self.handle_additive_expressions(left, right, node.operator)
            elif node.operator in ["*", "/", "and"]:
                return self.handle_multiplicative_expressions(
                    left, right, node.operator
                )
            elif node.operator in ["==", "!=", "<", ">", "<=", ">="]:
                return self.handle_relational_expressions(left, right, node.operator)

            # Invalid operation
            throw_invalid_operation_err(
                left.label,
                node.operator,
                right.label,
                self.node_start_pos,
                self.node_end_pos,
            )
        return left

    def handle_additive_expressions(self, left, right, op):
        """
        Handles additive expressions and returns the result of the operation
        @param left: The left operand of the expression
        @param right: The right operand of the expression
        @param op: The operation to be performed on the operands
        @return: A RunTimeObject representing the result of the operation
        """
        if op == "+":

            if left.label == "string" and left.label == right.label:  # String concat
                return RunTimeObject("string", left.value + right.value)
            elif left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value + right.value)

        elif op == "-":
            if left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value - right.value)

        elif op == "or":
            return RunTimeObject(left.label, left.value or right.value)

        # Invalid operation
        throw_invalid_operation_err(
            left.label, op, right.label, self.node_start_pos, self.node_end_pos
        )

    def handle_multiplicative_expressions(self, left, right, op):
        """
        Handles multiplicative expressions and returns the result of the operation
        as a runtime object
        @param left: The left operand of the expression
        @param right: The right operand of the expression
        @param op: The operation to be performed on the operands
        @return: A RunTimeObject representing the result of the operation
        """
        if op == "*":

            if (left.label == "string" and right.label == "number") or (
                left.label == "number" and right.label == "string"
            ):
                return RunTimeObject("string", left.value * right.value)
            elif left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value * right.value)

        elif op == "/":

            if left.label == "number" and left.label == right.label:
                if right.value != 0:
                    return RunTimeObject("number", left.value / right.value)
                else:
                    raise InterpreterError(
                        ErrorType.RUNTIME,
                        "Division by zero is not kawaii, please don't do that.",
                        self.node_start_pos,
                        self.node_end_pos,
                    )

        elif op == "and":
            return RunTimeObject(right.label, left.value and right.value)

        # Invalid operation
        throw_invalid_operation_err(
            left.label, op, right.label, self.node_start_pos, self.node_end_pos
        )

    def handle_relational_expressions(self, left, right, op):
        """
        Handles relational expressions and returns the result of the operation
        as a runtime object
        @param left: The left operand of the expression
        @param right: The right operand of the expression
        @param op: The operation to be performed on the operands
        @return: A RunTimeObject representing the result of the operation
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
        throw_invalid_operation_err(
            left.label, op, right.label, self.node_start_pos, self.node_end_pos
        )

    def visit_factor(self, node: "FactorNode"):
        """
        Visits a FactorNode and returns the result of the operation as a runtime object
        @param node: The FactorNode being visited
        @return: A RunTimeObject representing the result the evaluated factor
        """
        left_factor = node.left.accept(self)
        left_factor = self.__test_for_identifier(left_factor)

        if not node.right:
            return left_factor

        right_factor = node.right.accept(self)
        right_factor = self.__test_for_identifier(right_factor)
        if left_factor.value == "not":
            if right_factor.label in ["string", "number", "identifier", "boolean"]:
                return RunTimeObject("boolean", not right_factor.value)

            # Invalid operation
            throw_unary_type_err(
                left_factor.value,
                right_factor.value,
                self.node_start_pos,
                self.node_end_pos,
            )
        elif left_factor.value == "-":
            try:
                return RunTimeObject("number", -right_factor.value)
            except TypeError as e:
                raise InterpreterError(
                    ErrorType.TYPE,
                    e.args[0],
                    self.node_start_pos,
                    self.node_end_pos,
                )
        return left_factor

    @staticmethod
    def visit_operator(node: "OperatorNode"):
        """
        Visits an OperatorNode and returns the value as a runtime object
        @param node: The OperatorNode being visited
        @return: A RunTimeObject representing the value of the operator
        """
        return RunTimeObject("operator", node.value)

    @staticmethod
    def visit_identifier(node: "IdentifierNode"):
        """
        Visits an IdentifierNode and returns the name of the identifier as a runtime object
        @param node: The IdentifierNode being visited
        @return: A RunTimeObject representing the name of the identifier
        """
        return RunTimeObject("identifier", node.value)

    @staticmethod
    def visit_numeric_literal(node: "NumericLiteralNode"):
        """
        Visits a NumericLiteralNode and returns a runtime object representing a number.
        @param node: The NumericLiteralNode being visited
        @return: A RunTimeObject representing a number with the specified value
        """
        return RunTimeObject("number", node.value)

    @staticmethod
    def visit_string_literal(node: "StringLiteralNode"):
        """
        Visits a StringLiteralNode and returns a runtime object representing a string.
        @param node: The StringLiteralNode being visited
        @return: A RunTimeObject representing a string with the specified value
        """
        return RunTimeObject("string", node.value)

    @staticmethod
    def visit_boolean_literal(node: "BooleanNode"):
        """
        Visits a BooleanNode and returns a runtime object representing a boolean value.
        @param node: The BooleanNode being visited
        @return: A RunTimeObject representing a boolean with the specified value
        """
        return RunTimeObject("boolean", node.value)

    @staticmethod
    def generic_visit(node):
        """
        Called if no visitor function exists for the specified node.
        @param node: The node attempting to be visited
        """
        raise NotImplementedError(f"No visit_{node.label} method defined")

    def __test_for_identifier(
        self, runtime_object: "RunTimeObject", current_scope=False
    ):
        """
        Checks if the runtime object is an identifier, and returns
        the value held by the identifier
        @param runtime_object: The runtime object to test
        @return: The non-identifier runtime object
        """
        if runtime_object.label == "identifier":
            return self.current_env.lookup_variable(runtime_object.value, lookup_within_scope=current_scope)  # type: ignore
        else:
            return runtime_object

    def check_for_stack_overflow(self, node):
        """
        Checks if the recursion depth is exceeded.
        @param node: The current node being visited
        @raise InterpreterError: If the recursion depth is exceeded
        """
        if self.__recursion_count > INTERNAL_RECURSION_LIMIT:
            self.__recursion_count = 0
            raise InterpreterError(
                ErrorType.RECURSION,
                "Ara Ara!!!\nNon-kawaii recursion depth exceeded",
                node.start_pos,
                node.end_pos,
            )
        self.__recursion_count += 1
