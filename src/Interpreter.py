import sys
from typing import Optional, TextIO

from src.core.ASTNodes import (
    FileNode,
    Node,
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
    CharReprNode,
    LengthNode,
    IntReprNode,
)
from src.core.CacheMemory import cache_mem
from src.core.Environment import Environment
from src.core.RuntimeObject import RunTimeObject
from src.core.Symbol import VarSymbol, FunctionSymbol, FileSymbol
from src.core.Token import Position
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
INTERNAL_STACK_SIZE = 1010
SYS_RECURSION_LIMIT = 1000000


class Interpreter:
    def __init__(self, verbose: bool = False):
        self.__verbose = verbose
        self.global_env: Environment = Environment(name="global", level=1)
        self.current_env = self.global_env

        #  Control flow flags
        self.break_flag = False
        self.continue_flag = False
        self.return_flag = False
        self.return_value = None

        # Safety nets
        self.__visitor_depth = 0  # Keep track of the depth of the visitor
        self.__stack_pointer = 0  # Keep track of number of recursive function calls
        sys.setrecursionlimit(SYS_RECURSION_LIMIT)

        # Error handling
        self.node_start_pos = Position(line=-1, col=-1)
        self.node_end_pos = Position(line=-1, col=-1)

    def __log(self, message: str) -> None:
        if self.__verbose:
            print(message)

    def interpret(self, ast: Node):
        """
        Interprets the given abstract syntax tree by visiting the root node
        and returning the result of the interpretation
        """
        try:
            return ast.accept(self)
        except RecursionError as e:
            print(f"{emoji()}\nVisitor Error:", e, file=sys.stderr)
        except InterpreterError as e:
            print(e, file=sys.stderr)

    def visit(self, node: Node):
        """
        Visits a node and interprets it by calling the appropriate visit method
        and returning the result of the visit
        """
        if self.__visitor_depth >= MAX_VISIT_DEPTH:
            # visitor depth exceeded and an error should be thrown
            # to prevent the Python interpreter from a segfault
            raise RecursionError(
                "Visitor depth exceeded! You've ventured too far into the code jungle. "
                "Time to retreat before you're lost in the wild recursion! (¬‿¬)"
            )

        if not self.current_env:
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
        self.__log(warning_msg(f"Visited {node.label}"))

        self.__visitor_depth -= 1
        return result

    def visit_program(self, node: ProgramNode):
        """Interprets a program node by visiting its functions and body"""
        if node.eof:
            return

        for func in node.functions:
            func.accept(self)

        if node.body:
            node.body.accept(self)

    def visit_func_def(self, node: FuncDefNode):
        """
        Interprets a function definition node by adding the function
        and its properties to the symbol table of the current environment/scope
        """
        params = {}
        if node.args:
            for arg in node.args.accept(self):
                if arg.value not in params:
                    params[arg.value] = arg.label
                else:
                    raise InterpreterError(
                        ErrorType.RUNTIME,
                        f"Duplicate parameter {WARNING}'{arg.value}'",
                        node.args.start_pos,
                        node.args.end_pos,
                    )

        function_obj = RunTimeObject(
            "function", value=FunctionSymbol(node.identifier, params, node.body)
        )
        self.current_env.insert_symbol(
            node.identifier, VarSymbol(node.identifier, function_obj)
        )

    def visit_body(self, node: BodyNode):
        """
        Interprets a body node, executes its statements,
        and returns the result of the last evaluated statement
        """
        for stmt in node.statements:
            if self.break_flag or self.return_flag:
                break

            if self.continue_flag:
                self.continue_flag = False
                continue

            stmt.accept(self)

    def visit_return(self, node: ReturnNode):
        """
        Interprets a return statement node and
        returns the result of the evaluated expression if any
        """
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        self.return_value = node.expr.accept(self) if node.expr else None
        self.return_flag = True

    def visit_break(self, node: BreakNode):
        """Interprets a break statement node"""
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        self.break_flag = True

    def visit_continue(self, node: ContinueNode):
        """Interprets a continue statement node"""
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        self.continue_flag = True

    def __handle_conditional_execution(self, body_node: Optional[BodyNode]):
        """
        Handles the execution of a conditional body node
        and returns the result of the last evaluated statement (if any)
        """
        if not body_node:
            return

        body_node.accept(self)
        if self.return_flag:
            return self.return_value

    def visit_if(self, node: IfNode):
        """
        Visits an if node and interprets its body if the condition is met,
        and returns the result of the last evaluated statement (if any)
        """
        condition = node.expr.accept(self)
        if condition.value:
            return self.__handle_conditional_execution(node.body)

        for else_if_stmt in node.else_if_statements:
            condition = else_if_stmt.expr.accept(self)
            if condition.value:
                return self.__handle_conditional_execution(else_if_stmt.body)

        if node.else_body:
            return self.__handle_conditional_execution(node.else_body)

    def visit_while(self, node: WhileNode):
        """
        Visits a while loop and interprets its body while the condition is met,
        and returns the result of the last evaluated statement (if any)
        """
        condition = node.expr.accept(self)
        while condition.value:
            if stmt := self.__handle_conditional_execution(node.body):
                return stmt

            if self.break_flag:
                self.break_flag = False
                break

            condition = node.expr.accept(self)  # Re-evaluate condition

    def visit_for(self, node: ForNode):
        """
        Visits a for loop and interprets its body while the condition is met,
        and returns the result of the last evaluated statement (if any)
        @raise InterpreterError: If the range value is not an integer
        """

        def validate_range_node(range_node):
            """
            Validates the range value of a range node
            @raise InterpreterError: If the range value is not an integer.
            """
            runtime_object = range_node.accept(self)
            if not isinstance(runtime_object.value, int):
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
        iterator_runtime_object = RunTimeObject(label="number", value=0)
        self.current_env.insert_symbol(
            node.identifier.value,
            VarSymbol(node.identifier.value, iterator_runtime_object),
        )

        # incrementer to determine direction of iteration
        incrementer = 1 if range_start < range_end else -1
        for i in range(range_start, range_end, incrementer):
            iterator_runtime_object.value = i

            if self.break_flag:
                self.break_flag = False
                break

            if result := self.__handle_conditional_execution(node.body):
                return result

    def visit_array_def(self, node: ArrayNode):
        """Visits an ArrayNode and creates a new array in the symbol table"""
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos

        identifier = node.identifier
        if node.size:
            array_size = self.__test_for_identifier(node.size.accept(self)).value
            # FIXME: Handle nulls
            values = [RunTimeObject(label="number", value=0)] * int(array_size)
        elif node.initial_values:
            values = [value.accept(self) for value in node.initial_values]
        elif node.string_value:
            string_value = node.string_value.accept(self)
            values = [
                RunTimeObject("string", value=char) for char in string_value.value
            ]
        else:
            values = []

        array_symbol = RunTimeObject("array", values)
        self.current_env.insert_symbol(identifier, VarSymbol(identifier, array_symbol))

    def visit_array_access(self, node: ArrayNode):
        """
        Interprets an array access by visiting the array node
        and returning the value at the specified index
        """
        if not node.index:
            raise InterpreterError(
                ErrorType.RUNTIME,
                "No array index provided...",
                node.start_pos,
                node.end_pos,
            )

        identifier = node.identifier
        index = self.__test_for_identifier(node.index.accept(self)).value
        array = self.current_env.lookup_symbol(identifier).value

        if index < 0 or index >= len(array):
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Array index out of bounds",
                node.start_pos,
                node.end_pos,
            )

        return array[index]

    def visit_array_update(self, node: ArrayNode):
        """
        Interprets an array update by visiting the array node
        and updating the value at the specified index
        """
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos

        if not node.value:
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Value to amend to, not provided",
                self.node_start_pos,
                self.node_end_pos,
            )

        identifier = node.identifier
        index = self.__test_for_identifier(node.index.accept(self)).value
        value_runtime = node.value.accept(self)

        array_symbol = self.current_env.lookup_symbol(identifier).value
        if int(index) < 0 or int(index) >= len(array_symbol):
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Array index out of bounds",
                node.start_pos,
                node.end_pos,
            )

        array_symbol[index] = RunTimeObject(value_runtime.label, value_runtime.value)

    def visit_assignment(self, node: AssignmentNode):
        """
        Interprets a variable assignment by visiting the left and right nodes
        and assigning the value of the right node to the identifier in the left node
        """
        lhs = node.left.accept(self)
        rhs = node.right.accept(self)

        if rhs.label in "function":
            self.current_env.insert_symbol(lhs.value, VarSymbol(lhs.value, rhs))
        else:
            runtime_object = RunTimeObject(rhs.label, rhs.value)
            self.current_env.insert_symbol(
                lhs.value, VarSymbol(lhs.value, runtime_object)
            )

    def visit_call(self, node: CallNode):
        """
        Interprets a functional call, executes the function associated with the call node
        and returns the result of the function call
        """
        self.check_for_stack_overflow(node)

        function_symbol = self.current_env.lookup_symbol(node.identifier)
        if function_symbol.label != "function":
            raise InterpreterError(
                ErrorType.RUNTIME,
                f"'{node.identifier}' is not a function and cannot be called",
                node.start_pos,
                node.end_pos,
            )

        self.__stack_pointer += 1
        local_env = Environment(
            name=node.identifier,
            level=self.current_env.level + 1,
            parent=self.global_env,
        )
        old_env = self.current_env

        function_symbol = function_symbol.value
        if node.args:
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

            # assign arg values to local variables
            for i, param in enumerate(function_symbol.params):
                local_env.insert_symbol(param, VarSymbol(param, function_args[i]))
        self.current_env = local_env

        # Check cache for previously stored value, else walk through the function body
        env_hash = self.current_env.hash()
        result = cache_mem.get(env_hash)
        if result is None:
            function_symbol.body.accept(self)
            if self.return_flag:
                result = self.return_value
                self.return_flag = False
                self.return_value = None

            cache_mem.put(env_hash, result)

        self.current_env = old_env
        self.__stack_pointer -= 1
        return result

    @staticmethod
    def visit_input(node: InputNode):
        """Interprets input from the user and returns it when an input node is visited"""
        value = input(node.message)
        return RunTimeObject("string", value)

    def visit_print(self, node: PrintNode):
        """Interprets a print statement to the console"""
        args = node.args.accept(self)
        for i, arg in enumerate(args):
            spacing = " " if (i < len(args) - 1 and len(args) > 1) else ""
            runtime_value = arg.value
            print(runtime_value, end=spacing)

        if node.println:
            print()

    def visit_file_open(self, node: FileNode):
        """Interprets file open operation"""
        try:
            if not node.filepath:
                raise ValueError("File path must be provided...")
            elif not node.access_mode:
                raise ValueError("File access mode must be provided...")

            filepath_object = node.filepath.accept(self)
            access_mode_object = node.access_mode.accept(self)
            if not isinstance(filepath_object.value, str):
                raise TypeError("File path must be a string...")
            elif not isinstance(access_mode_object.value, str):
                raise TypeError("File access mode must be a string...")

            filepath = filepath_object.value
            access_mode = access_mode_object.value.lower()
            if access_mode not in ["r", "w", "a"]:
                raise ValueError(
                    "Invalid file access mode provided...\n"
                    "Valid Modes: 'r' (Read), 'w' (Write), 'a' (Append)"
                )

            try:
                file = open(filepath, access_mode)
            except IOError:
                raise

            file_object = RunTimeObject("file", FileSymbol(filepath, file))
            self.current_env.insert_symbol(
                node.identifier, VarSymbol(node.identifier, file_object)
            )
            log = f"File {filepath} opened with access mode '{access_mode}'"
            self.__log(success_msg(log))
        except (ValueError, TypeError, IOError) as e:
            raise InterpreterError(
                ErrorType.RUNTIME,
                e.args[0],
                node.start_pos,
                node.end_pos,
            )

    def visit_file_write(self, node: FileNode):
        """Interprets file write operation"""
        file_runtime_object = self.current_env.lookup_symbol(node.identifier)
        file_symbol = self.__test_for_identifier(file_runtime_object).value

        file: TextIO = file_symbol.file
        write_buffer_runtime_object = node.write_buffer.accept(self)
        buffer = write_buffer_runtime_object.value

        try:
            if file.closed:
                raise IOError("Cannot write to a closed file")

            if not file.writable():
                raise IOError("File is not writeable")

            if not isinstance(buffer, str) and not isinstance(buffer, list):
                raise IOError(f"Expected a string or array got {type(buffer)}")

            if isinstance(buffer, list):
                for item in buffer:
                    file.write(str(item.value))
            else:
                file.write(buffer)

            if node.is_write_line:
                file.write("\n")

            log = f"Message '{buffer}' written to file {file.name}"
            self.__log(success_msg(log))
        except IOError as e:
            raise InterpreterError(
                ErrorType.RUNTIME,
                e.args[0],
                node.start_pos,
                node.end_pos,
            )

    def visit_file_read(self, node: FileNode):
        """Interprets file read operation"""
        file_runtime_object = self.current_env.lookup_symbol(node.identifier)
        file_symbol = self.__test_for_identifier(file_runtime_object).value

        file: TextIO = file_symbol.file
        try:
            if file.closed:
                raise IOError("Cannot read from a closed file")

            if not file.readable():
                raise IOError("File is not readable")

            if node.n_chars_to_read:
                buffer = file.read(node.n_chars_to_read.accept(self).value)
            else:
                buffer = file.read()

            log = f"Message '{buffer}' read from file {file.name}"
            self.__log(success_msg(log))
            return RunTimeObject("string", buffer)
        except IOError as e:
            raise InterpreterError(
                ErrorType.RUNTIME, e.args[0], node.start_pos, node.end_pos
            )

    def visit_file_readline(self, node: FileNode):
        """Interprets file read line operation"""
        file_runtime_object = self.current_env.lookup_symbol(node.identifier)
        file_symbol = self.__test_for_identifier(file_runtime_object).value

        file: TextIO = file_symbol.file
        try:
            if file.closed:
                raise IOError("Cannot read from a closed file")

            if not file.readable():
                raise IOError("File is not readable")

            buffer = file.readline()
            log = f"Message '{buffer}' read from file {file.name}"
            self.__log(success_msg(log))
            return RunTimeObject("string", buffer)
        except IOError as e:
            raise InterpreterError(
                ErrorType.RUNTIME, e.args[0], node.start_pos, node.end_pos
            )

    def visit_file_close(self, node: FileNode):
        """Interprets file close operation"""
        runtime_object = self.current_env.lookup_symbol(node.identifier)
        file_symbol: FileSymbol = self.__test_for_identifier(runtime_object).value
        file = file_symbol.file

        try:
            file.close()
        except IOError as e:
            raise InterpreterError(
                ErrorType.RUNTIME, e.args[0], node.start_pos, node.end_pos
            )

        log = f"File {file.name} closed"
        self.__log(success_msg(log))

    def visit_char_repr(self, node: CharReprNode) -> RunTimeObject:
        """Interprets an ascii code and returns the character representation"""
        expression: RunTimeObject = node.expr.accept(self)
        if expression.label != "number":
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Expected a number representing a unicode character, got "
                + expression.label,
                node.start_pos,
                node.end_pos,
            )

        if expression.value < 0 or expression.value > 0x10FFFF:
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Expected a unicode character representation between 0 and 0x10FFFF, got "
                + str(expression.value),
                node.start_pos,
                node.end_pos,
            )
        return RunTimeObject("string", chr(expression.value))

    def visit_int_repr(self, node: IntReprNode) -> RunTimeObject:
        """Interprets a character and returns the ascii code representation"""
        expression: RunTimeObject = node.expr.accept(self)
        if expression.label != "string" or len(expression.value) != 1:
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Expected a string representing a unicode character, got "
                + expression.label,
                node.start_pos,
                node.end_pos,
            )

        try:
            return RunTimeObject("number", ord(expression.value))
        except ValueError:
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Expected a unicode character representation between 0 and 0x10FFFF, got "
                + str(expression.value),
                node.start_pos,
                node.end_pos,
            )

    def visit_length(self, node: LengthNode) -> RunTimeObject:
        """Interprets a length expression and returns the result of the operation"""
        expression: RunTimeObject = node.expr.accept(self)
        if expression.label != "string" and expression.label != "array":
            raise InterpreterError(
                ErrorType.RUNTIME,
                "Expected a string or array, got " + expression.label,
                node.start_pos,
                node.end_pos,
            )
        return RunTimeObject("number", len(expression.value))

    def visit_postfix_expr(self, node: PostfixExprNode) -> RunTimeObject:
        """Interprets a postfix expression and returns the result of the operation"""
        lhs = node.left.accept(self)
        runtime_object = self.__test_for_identifier(lhs)
        runtime_object.value += 1 if node.operator == "++" else -1
        return RunTimeObject("number", runtime_object.value)

    def visit_args(self, node: ArgsNode) -> list[RunTimeObject]:
        """
        Interprets the arguments of a function call and returns a list of runtime objects
        representing the arguments passed to the function call
        """
        return [arg_node.accept(self) for arg_node in node.children]

    def visit_expr(self, node: ExprNode) -> RunTimeObject:
        """Interprets an expression and returns the result of the evaluated expression"""
        self.node_start_pos = node.start_pos
        self.node_end_pos = node.end_pos
        return self.handle_expressions(node)

    def visit_simple_expr(self, node: SimpleExprNode) -> RunTimeObject:
        """Interprets a simple expression and returns the result of the evaluated expression"""
        return self.handle_expressions(node)

    def visit_term(self, node: TermNode) -> RunTimeObject:
        """Interprets a term expression and returns the result of the evaluated expression"""
        return self.handle_expressions(node)

    def handle_expressions(self, node: ExprNode) -> RunTimeObject:
        """
        Handles expressions and returns a runtime object representing the result of the operation
        """
        left = node.left.accept(self)
        left = self.__test_for_identifier(left)

        if node.operator:
            right = node.right.accept(self)
            right = self.__test_for_identifier(right)

            # Handle operation
            if node.operator in ["+", "-", "or"]:
                return self.handle_additive_expressions(left, right, node.operator)
            elif node.operator in ["*", "/", "and", "%"]:
                return self.handle_multiplicative_expressions(
                    left, right, node.operator
                )
            elif node.operator in ["==", "!=", "<", ">", "<=", ">="]:
                return self.handle_relational_expressions(left, right, node.operator)

            # Invalid operation
            return throw_invalid_operation_err(
                left.label,
                node.operator,
                right.label,
                self.node_start_pos,
                self.node_end_pos,
            )
        return left

    def handle_additive_expressions(
        self, left: RunTimeObject, right: RunTimeObject, op: str
    ) -> RunTimeObject:
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
        return throw_invalid_operation_err(
            left.label, op, right.label, self.node_start_pos, self.node_end_pos
        )

    def handle_multiplicative_expressions(
        self, left: RunTimeObject, right: RunTimeObject, op: str
    ) -> RunTimeObject:
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

        elif op == "%":
            if left.label == "number" and left.label == right.label:
                return RunTimeObject("number", left.value % right.value)

        # Invalid operation
        return throw_invalid_operation_err(
            left.label, op, right.label, self.node_start_pos, self.node_end_pos
        )

    def handle_relational_expressions(
        self, left: RunTimeObject, right: RunTimeObject, op: str
    ) -> RunTimeObject:
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
                res = eval(f"{repr(left.value)} {op} {repr(right.value)}")
            else:
                res = eval(f"{left.value} {op} {right.value}")
            return RunTimeObject("boolean", res)

        # Invalid operation
        return throw_invalid_operation_err(
            left.label, op, right.label, self.node_start_pos, self.node_end_pos
        )

    def visit_factor(self, node: FactorNode) -> RunTimeObject:
        """Visits a FactorNode and returns the value as a runtime object"""
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
            return throw_unary_type_err(
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
                    ErrorType.TYPE, e.args[0], self.node_start_pos, self.node_end_pos
                )
        return left_factor

    @staticmethod
    def visit_operator(node: OperatorNode) -> RunTimeObject:
        return RunTimeObject("operator", node.value)

    @staticmethod
    def visit_identifier(node: IdentifierNode) -> RunTimeObject:
        return RunTimeObject("identifier", node.value)

    @staticmethod
    def visit_numeric_literal(node: NumericLiteralNode) -> RunTimeObject:
        return RunTimeObject("number", node.value)

    @staticmethod
    def visit_string_literal(node: StringLiteralNode) -> RunTimeObject:
        return RunTimeObject("string", node.value)

    @staticmethod
    def visit_boolean_literal(node: BooleanNode) -> RunTimeObject:
        return RunTimeObject("boolean", node.value)

    @staticmethod
    def generic_visit(node: Node):
        raise NotImplementedError(f"No visit_{node.label} method defined")

    def __test_for_identifier(
        self, runtime_object: RunTimeObject, current_scope=False
    ) -> RunTimeObject:
        """Checks if the runtime object is an identifier, and returns its value"""
        if runtime_object.label != "identifier":
            return runtime_object

        return self.current_env.lookup_symbol(
            runtime_object.value, lookup_within_scope=current_scope
        )

    def check_for_stack_overflow(self, node: CallNode):
        """
        Checks if the stack pointer has exceeded the internal stack size.
        @raise InterpreterError: If the stack pointer has exceeded the internal stack size
        """
        if self.__stack_pointer > INTERNAL_STACK_SIZE:
            self.__stack_pointer = 0
            raise InterpreterError(
                ErrorType.RECURSION,
                "Ara Ara!!!\nNon-kawaii recursion depth exceeded",
                node.start_pos,
                node.end_pos,
            )
        self.__stack_pointer += 1
