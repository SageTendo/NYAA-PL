from pathlib import Path
import sys
from typing import Optional

from src.Lexer import Lexer
from src.core.ASTNodes import (
    BodyNode,
    Node,
    ReturnNode,
    ProgramNode,
    SimpleExprNode,
    AssignmentNode,
    IdentifierNode,
    PostfixExprNode,
    PrintNode,
    ArgsNode,
    NumericLiteralNode,
    StringLiteralNode,
    BooleanNode,
    FactorNode,
    ExprNode,
    CallNode,
    InputNode,
    BreakNode,
    ContinueNode,
    WhileNode,
    IfNode,
    ElifNode,
    FuncDefNode,
    TermNode,
    OperatorNode,
    ForNode,
    ArrayNode,
    FileNode,
)
from src.core.Token import Token
from src.core.Types import TokenType
from src.utils.ErrorHandler import (
    success_msg,
    warning_msg,
    throw_unexpected_token_err,
    ParserError,
    LexerError,
)


class Parser:
    def __init__(self, *, lexer: Lexer, verbose=False):
        self.curr_tkn: Token = Token()
        self.__lexer = lexer
        self.__verbose = verbose

    def __log(self, msg, success=True) -> None:
        """
        Log a message to the console
        @param msg: The message to display
        @param success: Whether the message is a success message or not
        """
        if not self.__verbose:
            return

        message = success_msg(msg) if success else warning_msg(msg)
        print(message)

    def __expected_token(self, expected_type: TokenType) -> bool:
        return self.curr_tkn.type == expected_type

    def __peek_token(self) -> Token:
        """Peek at the next token to be parsed"""
        return self.__lexer.peek_token()

    def __expect_and_consume(self, expected_type: TokenType) -> None:
        """
        Checks the current token type matches the expected type.
        Consume the token if it matches, otherwise report an error.
        """
        if not self.__expected_token(expected_type):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                expected_type.__str__(),
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )
        self.__consume_token()

    def __expect_and_consume_op(self) -> None:
        """
        Check the current token is of an operator type.
        Consume the token if it matches, otherwise throw an error
        """
        if not (TokenType.bin_op(self.curr_tkn) or TokenType(self.curr_tkn.type)):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[OPERATOR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )
        self.__consume_token()

    def __consume_token(self) -> None:
        """
        Consumes the current token and prepares the next token to be parsed
        """
        self.__log(f"Consuming {self.curr_tkn}...", success=False)
        self.curr_tkn = self.__lexer.get_token()

    def __handle_op_token(self) -> str:
        """
        Handles expression operator tokens and
        returns the respective operator to perform
        """
        token_type = self.curr_tkn.type
        self.__expect_and_consume_op()

        if token_type == TokenType.PLUS:
            return "+"
        elif token_type == TokenType.MINUS:
            return "-"
        elif token_type == TokenType.MULTIPLY:
            return "*"
        elif token_type == TokenType.DIVIDE:
            return "/"
        elif token_type == TokenType.AND:
            return "and"
        elif token_type == TokenType.OR:
            return "or"
        elif token_type == TokenType.LT:
            return "<"
        elif token_type == TokenType.GT:
            return ">"
        elif token_type == TokenType.LTE:
            return "<="
        elif token_type == TokenType.GTE:
            return ">="
        elif token_type == TokenType.EQ:
            return "=="
        elif token_type == TokenType.NEQ:
            return "!="
        else:
            return throw_unexpected_token_err(
                token_type,
                "[OPERATOR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

    def parse_program(self) -> ProgramNode:
        """program: funcDef* MAIN LPAR RPAR TO (LBRACE body RBRACE | statement ';') | EOF;"""
        program_node = ProgramNode()
        program_node.start_pos = self.curr_tkn.position

        if self.curr_tkn.type == TokenType.ENDMARKER:
            program_node.set_eof()
            program_node.end_pos = self.curr_tkn.position
            return program_node

        # parse function definitions
        while self.curr_tkn.type == TokenType.DEF:
            program_node.append_func(self.parse_func_def())

        self.__expect_and_consume(TokenType.MAIN)
        self.__expect_and_consume(TokenType.LPAR)
        self.__expect_and_consume(TokenType.RPAR)
        self.__expect_and_consume(TokenType.TO)

        # Parse single statement or multiple statements
        if TokenType.statement_start(self.curr_tkn):
            program_node.set_body(self.parse_body())
            self.__expect_and_consume(TokenType.SEMICOLON)
        else:
            #  { body* }
            self.__expect_and_consume(TokenType.LBRACE)
            program_node.set_body(self.parse_body())
            self.__expect_and_consume(TokenType.RBRACE)

        self.__expect_and_consume(TokenType.ENDMARKER)
        program_node.end_pos = self.curr_tkn.position
        return program_node

    def parse_body(self) -> BodyNode:
        """body:   statement*"""
        self.__log("<Body>")

        body = BodyNode()
        start_pos = self.curr_tkn.position
        while TokenType.statement_start(self.curr_tkn):
            body.append(self.parse_statement())

        self.__log("</Body>")
        body.start_pos = start_pos
        body.end_pos = self.curr_tkn.position
        return body

    def parse_conditional_body(self) -> Node:
        """conditionalBody:  statement conditionalBody? | BREAK | CONTINUE"""
        self.__log("<ConditionalBody>")
        body = BodyNode()
        body.start_pos = self.curr_tkn.position

        while TokenType.statement_start(self.curr_tkn):
            body.append(self.parse_statement())

        if self.__expected_token(TokenType.BREAK):
            self.__expect_and_consume(TokenType.BREAK)
            body.append(BreakNode())
        elif self.__expected_token(TokenType.CONTINUE):
            self.__expect_and_consume(TokenType.CONTINUE)
            body.append(ContinueNode())

        self.__log("</ConditionalBody>")
        body.end_pos = self.curr_tkn.position
        return body

    def parse_statement(self) -> Node:
        """
        statement:  PASS | retStatement | assignmentStatement
                    | whileStatement | ifStatement | printStatement
                    | inputStatement | callStatement | postfixStatement
        """
        start_pos = self.curr_tkn.position

        if self.__expected_token(TokenType.RET):
            statement_node = self.parse_return()

        elif self.__expected_token(TokenType.ID):
            if self.__peek_token().type == TokenType.ASSIGN:
                statement_node = self.parse_assignment()

            elif TokenType.postfix(self.__peek_token()):
                statement_node = self.parse_postfix()

            elif self.__peek_token().type == TokenType.LPAR:
                statement_node = self.parse_func_call()

            elif self.__peek_token().type == TokenType.TO:
                statement_node = self.parse_pointer_assignment()

            elif self.__peek_token().type == TokenType.LBRACKET:
                statement_node = self.parse_array_assignment()

            else:
                self.__expect_and_consume(TokenType.ID)
                return throw_unexpected_token_err(
                    self.curr_tkn.type,
                    "[ASSIGNMENT_TYPE or POSTFIX_TYPE or FUNC_CALL_TYPE]",
                    self.curr_tkn.line_num,
                    self.curr_tkn.column_num,
                )
        else:
            if self.__expected_token(TokenType.WHILE):
                statement_node = self.parse_while()
            elif self.__expected_token(TokenType.FOR):
                statement_node = self.parse_for()
            elif self.__expected_token(TokenType.IF):
                statement_node = self.parse_if()
            elif TokenType.callable(self.curr_tkn):
                statement_node = self.parse_callable()
            else:
                return throw_unexpected_token_err(
                    self.curr_tkn.type,
                    "[STATEMENT_TYPE]",
                    self.curr_tkn.line_num,
                    self.curr_tkn.column_num,
                )

        statement_node.start_pos = start_pos
        statement_node.end_pos = self.curr_tkn.position
        return statement_node

    def parse_pointer_assignment(self):
        """PointerAssignment: ID TO array_def | file_open"""
        pointer_node = Node("null")
        pointer_node.start_pos = self.curr_tkn.position

        identifier = self.curr_tkn.word
        self.__expect_and_consume(TokenType.ID)
        self.__expect_and_consume(TokenType.TO)

        match self.curr_tkn.type:
            case TokenType.LBRACE | TokenType.LBRACKET:
                pointer_node = self.parse_array_def(identifier=identifier)
            case TokenType.FILE_OPEN:
                pointer_node = self.parse_file_open(identifier=identifier)
            case _:
                return throw_unexpected_token_err(
                    self.curr_tkn.type,
                    "[ARRAY_DEF_TYPE or FILE_OPEN_TYPE]",
                    self.curr_tkn.line_num,
                    self.curr_tkn.column_num,
                )

        pointer_node.end_pos = self.curr_tkn.position
        return pointer_node

    def parse_func_def(self) -> FuncDefNode:
        """
        FuncDef:  DEF ID args TO (LBRACE body RBRACE | statement ';')
        """
        start_pos = self.curr_tkn.position
        self.__expect_and_consume(TokenType.DEF)
        identifier = self.curr_tkn.word
        self.__expect_and_consume(TokenType.ID)

        args: Optional[ArgsNode] = None
        if self.__peek_token().type == TokenType.RPAR:
            self.__expect_and_consume(TokenType.LPAR)
            self.__expect_and_consume(TokenType.RPAR)
        else:
            args = self.parse_params()
        self.__expect_and_consume(TokenType.TO)
        if TokenType.statement_start(self.curr_tkn):
            body = self.parse_body()
        else:
            self.__expect_and_consume(TokenType.LBRACE)
            body = self.parse_body()
            self.__expect_and_consume(TokenType.RBRACE)

        func_def_node = FuncDefNode(identifier, args, body)
        func_def_node.start_pos = start_pos
        func_def_node.end_pos = self.curr_tkn.position
        return func_def_node

    def parse_func_call(self) -> CallNode:
        """funcCall: ID args"""
        self.__log("<FuncCall>")

        identifier = self.curr_tkn.word
        start_pos = self.curr_tkn.position
        self.__expect_and_consume(TokenType.ID)
        args = self.parse_args()

        self.__log("</FuncCall>")
        call_node = CallNode(identifier, args)
        call_node.start_pos = start_pos
        call_node.end_pos = self.curr_tkn.position
        return call_node

    def parse_postfix(self) -> PostfixExprNode:
        """PostfixExpr: ID (UN_ADD | UN_SUB)"""
        self.__log("<Postfix>")

        start_pos = self.curr_tkn.position
        left_node = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)

        op = self.curr_tkn.type
        if op == TokenType.UN_ADD:
            self.__expect_and_consume(TokenType.UN_ADD)
            postfix_node = PostfixExprNode(left_node, "++")
        elif op == TokenType.UN_SUB:
            self.__expect_and_consume(TokenType.UN_SUB)
            postfix_node = PostfixExprNode(left_node, "--")
        else:
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[UN_ADD or UN_SUB]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        self.__log("</Postfix>")
        postfix_node.start_pos = start_pos
        postfix_node.end_pos = self.curr_tkn.position
        return postfix_node

    def parse_index(self) -> ExprNode:
        """Index: [ simple_expr ]"""
        self.__log("<Index>")

        self.__expect_and_consume(TokenType.LBRACKET)
        simple_expr = self.parse_simple_expr()
        self.__expect_and_consume(TokenType.RBRACKET)

        self.__log("</Index>")
        return simple_expr

    def parse_array_def(self, identifier: str) -> ArrayNode:
        """ArrayDef: [ expr ] | { values* }"""
        self.__log("<ArrDef>")
        start_pos = self.curr_tkn.position

        size = None
        values: list[ExprNode] = []
        if self.__expected_token(TokenType.LBRACKET):
            self.__expect_and_consume(TokenType.LBRACKET)
            size = self.parse_simple_expr()
            self.__expect_and_consume(TokenType.RBRACKET)

        elif self.__expected_token(TokenType.LBRACE):
            self.__expect_and_consume(TokenType.LBRACE)
            while not self.__expected_token(TokenType.RBRACE):
                values.append(self.parse_expr())
                if self.__expected_token(TokenType.COMMA):
                    self.__expect_and_consume(TokenType.COMMA)
            self.__expect_and_consume(TokenType.RBRACE)

        self.__log("<ArrDef>")
        array_node = ArrayNode(
            label="array_def", identifier=identifier, size=size, initial_values=values
        )
        array_node.start_pos = start_pos
        array_node.end_pos = self.curr_tkn.position
        return array_node

    def parse_file_open(self, identifier: str) -> FileNode:
        """FileDef: FILE_OPEN LPAR ID COMMA MODE RPAR"""
        start_pos = self.curr_tkn.position
        self.__expect_and_consume(TokenType.FILE_OPEN)
        self.__expect_and_consume(TokenType.LPAR)
        filepath = self.parse_expr()

        self.__expect_and_consume(TokenType.COMMA)
        access_mode = self.parse_expr()
        self.__expect_and_consume(TokenType.RPAR)
        file_node = FileNode(
            label="file_open",
            identifier=identifier,
            filepath=filepath,
            access_mode=access_mode,
        )

        file_node.start_pos = start_pos
        file_node.end_pos = self.curr_tkn.position
        return file_node

    def parse_array_access(self) -> ArrayNode:
        """ArrayAccess: ID index"""
        self.__log("<ArrayAccess>")

        start_pos = self.curr_tkn.position
        identifier = self.curr_tkn.word
        self.__expect_and_consume(TokenType.ID)
        index = self.parse_index()

        self.__log("</ArrayAccess>")
        array_node = ArrayNode(label="array_access", identifier=identifier, index=index)
        array_node.start_pos = start_pos
        array_node.end_pos = self.curr_tkn.position
        return array_node

    def parse_array_assignment(self) -> ArrayNode:
        """ArrayAssignment: ID index ASSIGN expr"""
        self.__log("<ArrayAssign>")

        start_pos = self.curr_tkn.position
        identifier = self.curr_tkn.word
        self.__expect_and_consume(TokenType.ID)
        index = self.parse_index()
        self.__expect_and_consume(TokenType.ASSIGN)
        expression = self.parse_expr()

        self.__log("</ArrayAssign>")
        array_node = ArrayNode(
            label="array_update", identifier=identifier, index=index, value=expression
        )
        array_node.start_pos = start_pos
        array_node.end_pos = self.curr_tkn.position
        return array_node

    def parse_assignment(self) -> AssignmentNode:
        """Assignment: ID ASSIGN (expr | callable)"""
        self.__log("<Assignment>")

        start_pos = self.curr_tkn.position
        left_node = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)

        self.__expect_and_consume(TokenType.ASSIGN)
        if (
            TokenType.callable(self.curr_tkn)
            and self.__peek_token().type == TokenType.LPAR
        ):
            right_node = self.parse_callable()
        else:
            right_node = self.parse_expr()

        self.__log("<Assignment>")
        assignment_node = AssignmentNode(left_node, right_node)
        assignment_node.start_pos = start_pos
        assignment_node.end_pos = self.curr_tkn.position
        return assignment_node

    def parse_while(self) -> WhileNode:
        """WhileStatement: WHILE ( expr ) { ( body | BREAK | CONTINUE) }"""
        self.__log("<While>")
        start_pos = self.curr_tkn.position

        right_node = None
        self.__expect_and_consume(TokenType.WHILE)
        self.__expect_and_consume(TokenType.LPAR)
        left_node = self.parse_expr()
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            right_node = self.parse_conditional_body()
        self.__expect_and_consume(TokenType.RBRACE)

        self.__log("</While>")
        while_node = WhileNode(left_node, right_node)
        while_node.start_pos = start_pos
        while_node.end_pos = self.curr_tkn.position
        return while_node

    def parse_for(self) -> ForNode:
        """ForStatement: FOR ID TO ( NUM, NUM ) { body }"""
        self.__log("<For>")
        start_pos = self.curr_tkn.position

        body = None
        self.__expect_and_consume(TokenType.FOR)
        identifier = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)
        self.__expect_and_consume(TokenType.TO)

        self.__expect_and_consume(TokenType.LPAR)
        range_start = self.parse_expr()
        self.__expect_and_consume(TokenType.COMMA)
        range_end = self.parse_expr()
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            body = self.parse_conditional_body()
        self.__expect_and_consume(TokenType.RBRACE)

        self.__log("</For>")
        for_node = ForNode(identifier, range_start, range_end, body)
        for_node.start_pos = start_pos
        for_node.end_pos = self.curr_tkn.position
        return for_node

    def parse_if(self) -> IfNode:
        """IfStatement: IF ( expr ) { body }"""
        self.__log("<If>")
        start_pos = self.curr_tkn.position

        body_node = None
        self.__expect_and_consume(TokenType.IF)
        self.__expect_and_consume(TokenType.LPAR)
        expr_node = self.parse_expr()
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            body_node = self.parse_conditional_body()
        self.__expect_and_consume(TokenType.RBRACE)

        # Parse elif and else statements
        if_node = IfNode(expr_node, body_node)
        while self.__expected_token(TokenType.ELIF):
            if_node.append_else_if(self.parse_elif())

        if self.__expected_token(TokenType.ELSE):
            if_node.set_else_body(self.parse_else())

        self.__log("</If>")
        if_node.start_pos = start_pos
        if_node.end_pos = self.curr_tkn.position
        return if_node

    def parse_elif(self) -> ElifNode:
        """ElifStatement: ELIF ( expr ) { body }"""
        self.__log("<Elif>")
        start_pos = self.curr_tkn.position
        body_node = None

        self.__expect_and_consume(TokenType.ELIF)
        self.__expect_and_consume(TokenType.LPAR)
        expr_node = self.parse_expr()
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            body_node = self.parse_conditional_body()
        self.__expect_and_consume(TokenType.RBRACE)

        self.__log("</Elif>")
        elif_node = ElifNode(expr_node, body_node)
        elif_node.start_pos = start_pos
        elif_node.end_pos = self.curr_tkn.position
        return elif_node

    def parse_else(self) -> Optional[Node]:
        """ElseStatement: ELSE { body }"""
        self.__log("<Else>")

        body = None
        self.__expect_and_consume(TokenType.ELSE)
        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            body = self.parse_conditional_body()
        self.__expect_and_consume(TokenType.RBRACE)

        self.__log("</Else>")
        return body

    def parse_return(self) -> ReturnNode:
        """ReturnStatement: RETURN expr?"""
        self.__log("<Return>")
        start_pos = self.curr_tkn.position

        self.__expect_and_consume(TokenType.RET)
        return_node = ReturnNode()
        if (
            TokenType.expression(self.curr_tkn)
            and self.__peek_token().type != TokenType.ASSIGN
        ):
            return_node.set_expr(self.parse_expr())

        self.__log("</Return>")
        return_node.start_pos = start_pos
        return_node.end_pos = self.curr_tkn.position
        return return_node

    def parse_print(self, print_ln=False) -> PrintNode:
        """PrintStatement: PRINT args"""
        self.__log("<Print>")
        start_pos = self.curr_tkn.position

        # PrintlnStatement: PRINTLN args
        if self.curr_tkn.type == TokenType.PRINTLN:
            self.__expect_and_consume(TokenType.PRINTLN)
            print_ln = True
        else:
            self.__expect_and_consume(TokenType.PRINT)

        args = self.parse_args()
        print_node = PrintNode(args, print_ln)

        self.__log("</Print>")
        print_node.start_pos = start_pos
        print_node.end_pos = self.curr_tkn.position
        return print_node

    def parse_input(self) -> InputNode:
        """InputStatement: INPUT (STR)?"""
        self.__log("<Input>")
        start_pos = self.curr_tkn.position

        self.__expect_and_consume(TokenType.INPUT)
        self.__expect_and_consume(TokenType.LPAR)

        msg = None
        if self.__expected_token(TokenType.STR):
            msg = self.curr_tkn.word
            self.__expect_and_consume(TokenType.STR)
        self.__expect_and_consume(TokenType.RPAR)
        input_node = InputNode(msg)

        self.__log("</Input>")
        input_node.start_pos = start_pos
        input_node.end_pos = self.curr_tkn.position
        return input_node

    def parse_params(self) -> ArgsNode:
        """params: param (',' param)*"""
        self.__log("<Params>")
        params = ArgsNode()
        params.start_pos = self.curr_tkn.position

        self.__expect_and_consume(TokenType.LPAR)
        if not (
            self.__expected_token(TokenType.ID) or self.__expected_token(TokenType.RPAR)
        ):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[ID or RPAR]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        if self.__expected_token(TokenType.ID):
            self.__log("<Param>")
            params.append(IdentifierNode(self.curr_tkn))
            self.__expect_and_consume(TokenType.ID)
            self.__log("</Param>")

            while self.__expected_token(TokenType.COMMA):
                self.__expect_and_consume(TokenType.COMMA)

                self.__log("<Param>")
                params.append(IdentifierNode(self.curr_tkn))
                self.__expect_and_consume(TokenType.ID)
                self.__log("</Param>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__log("</Params>")
        params.end_pos = self.curr_tkn.position
        return params

    def parse_args(self) -> ArgsNode:
        """args: arg (',' arg)*"""
        self.__log("<Args>")
        args = ArgsNode()
        args.start_pos = self.curr_tkn.position

        self.__expect_and_consume(TokenType.LPAR)
        if TokenType.expression(self.curr_tkn) or TokenType.callable(self.curr_tkn):
            args.append(self.parse_arg())

            while self.__expected_token(TokenType.COMMA):
                self.__expect_and_consume(TokenType.COMMA)
                args.append(self.parse_arg())
        self.__expect_and_consume(TokenType.RPAR)

        self.__log("</Args>")
        args.end_pos = self.curr_tkn.position
        return args

    def parse_arg(self):
        """arg: callable | expr"""
        self.__log("<Arg>")

        if self.__peek_token().type == TokenType.LPAR:
            arg = self.parse_callable()
        else:
            arg = self.parse_expr()

        self.__log("</Arg>")
        return arg

    def parse_callable(self) -> ExprNode:
        """callable: PRINT | INPUT | ID args"""
        self.__log("<Callable>")

        is_print_token = self.__expected_token(TokenType.PRINT)
        is_print_token |= self.__expected_token(TokenType.PRINTLN)
        if is_print_token:
            call_node = self.parse_print()
        elif self.__expected_token(TokenType.INPUT):
            call_node = self.parse_input()
        elif TokenType.file_IO(self.curr_tkn):
            call_node = self.parse_file_IO()
        elif self.__expected_token(TokenType.ID):
            call_node = self.parse_func_call()
        else:
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "CALLABLE_TYPE",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        self.__log("</Callable>")
        return call_node

    def parse_file_IO(self) -> FileNode:
        """File IO: FILE_OPEN | FILE_CLOSE | FILE_READ | FILE_READLINE | FILE_WRITE | FILE_WRITELINE"""
        self.__log("<FileIO>")
        start_pos = self.curr_tkn.position

        match self.curr_tkn.type:
            case TokenType.FILE_CLOSE:
                self.__expect_and_consume(TokenType.FILE_CLOSE)
                self.__expect_and_consume(TokenType.LPAR)
                identifier = self.curr_tkn.word
                self.__expect_and_consume(TokenType.ID)

                self.__expect_and_consume(TokenType.RPAR)
                file_node = FileNode(label="file_close", identifier=identifier)
            case TokenType.FILE_READ:
                self.__expect_and_consume(TokenType.FILE_READ)
                self.__expect_and_consume(TokenType.LPAR)
                identifier = self.curr_tkn.word
                self.__expect_and_consume(TokenType.ID)
                self.__expect_and_consume(TokenType.COMMA)

                n_chars_to_read = None
                if TokenType.expression(self.curr_tkn):
                    n_chars_to_read = self.parse_expr()
                self.__expect_and_consume(TokenType.RPAR)

                file_node = FileNode(
                    label="file_read",
                    identifier=identifier,
                    n_chars_to_read=n_chars_to_read,
                )
            case TokenType.FILE_READLINE:
                self.__expect_and_consume(TokenType.FILE_READLINE)
                self.__expect_and_consume(TokenType.LPAR)
                identifier = self.curr_tkn.word
                self.__expect_and_consume(TokenType.ID)
                self.__expect_and_consume(TokenType.RPAR)

                file_node = FileNode(
                    label="file_readline",
                    identifier=identifier,
                )
            case TokenType.FILE_WRITE | TokenType.FILE_WRITELINE:
                if self.__expected_token(TokenType.FILE_WRITE):
                    self.__expect_and_consume(TokenType.FILE_WRITE)
                    label = "file_write"
                else:
                    self.__expect_and_consume(TokenType.FILE_WRITELINE)
                    label = "file_writeline"

                self.__expect_and_consume(TokenType.LPAR)
                identifier = self.curr_tkn.word
                self.__expect_and_consume(TokenType.ID)
                self.__expect_and_consume(TokenType.COMMA)

                write_buffer = self.parse_expr()
                self.__expect_and_consume(TokenType.RPAR)

                file_node = FileNode(
                    label=label, identifier=identifier, write_buffer=write_buffer
                )
            case _:
                return throw_unexpected_token_err(
                    self.curr_tkn.type,
                    "FILE_IO_TYPE",
                    self.curr_tkn.line_num,
                    self.curr_tkn.column_num,
                )
        self.__log("</FileIO>")
        file_node.start_pos = start_pos
        file_node.end_pos = self.curr_tkn.position
        return file_node

    def parse_expr(self) -> ExprNode:
        """expr: simpleExpr | simpleExpr relationalOp simpleExpr"""
        self.__log("<Expr>")
        expr_node = ExprNode()
        expr_node.start_pos = self.curr_tkn.position

        if not TokenType.expression(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[EXPRESSION_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        expr_node.left = self.parse_simple_expr()
        if TokenType.rel_op(self.curr_tkn):
            expr_node.operator = self.__handle_op_token()
            expr_node.right = self.parse_expr()

        expr_node.end_pos = self.curr_tkn.position
        self.__log("</Expr>")
        return expr_node

    def parse_simple_expr(self) -> ExprNode:
        """simpleExpr: term | term addOp simpleExpr"""
        self.__log("<SimpleExpr>")
        start_pos = self.curr_tkn.position

        if not TokenType.term(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[SIMPLE_EXPR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        left = self.parse_term()
        while TokenType.add_op(self.curr_tkn):
            op = self.__handle_op_token()
            right = self.parse_term()
            left = SimpleExprNode(left, right, op)

        self.__log("</SimpleExpr>")
        left.start_pos = start_pos
        left.end_pos = self.curr_tkn.position
        return left

    def parse_term(self) -> ExprNode:
        """term: factor | factor mulOp terme"""
        self.__log("<Term>")
        start_pos = self.curr_tkn.position

        if not TokenType.factor(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[TERM_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        left = self.parse_factor()
        while TokenType.mul_op(self.curr_tkn):
            op = self.__handle_op_token()
            right = self.parse_factor()
            left = TermNode(left, right, op)

        self.__log("</Term>")
        left.start_pos = start_pos
        left.end_pos = self.curr_tkn.position
        return left

    def parse_factor(self) -> ExprNode:
        """
        factor: ID | INT | INT '.' INT | STR
                | TRUE | FALSE | LPAR expr RPAR
                | NOT factor | NEG factor | Func_Call
        """
        self.__log("<Factor>")

        if not TokenType.factor(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[FACTOR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        if self.__expected_token(TokenType.ID):
            if self.__peek_token().type == TokenType.LPAR:
                factor_node = FactorNode(self.parse_func_call())

            elif self.__peek_token().type == TokenType.LBRACKET:
                start_pos = self.curr_tkn.position
                array_access_node = self.parse_array_access()
                array_access_node.start_pos = start_pos
                array_access_node.end_pos = self.curr_tkn.position
                factor_node = FactorNode(array_access_node)

            else:
                factor_node = IdentifierNode(self.curr_tkn)
                self.__expect_and_consume(TokenType.ID)

        elif self.__expected_token(TokenType.INT) or self.__expected_token(
            TokenType.FLOAT
        ):
            factor_node = NumericLiteralNode(self.curr_tkn)
            if self.curr_tkn.type == TokenType.INT:
                self.__expect_and_consume(TokenType.INT)
            else:
                self.__expect_and_consume(TokenType.FLOAT)

        elif self.__expected_token(TokenType.STR):
            factor_node = StringLiteralNode(self.curr_tkn)
            self.__expect_and_consume(TokenType.STR)

        elif self.__expected_token(TokenType.TRUE) or self.__expected_token(
            TokenType.FALSE
        ):
            if self.curr_tkn.type == TokenType.TRUE:
                self.__expect_and_consume(TokenType.TRUE)
                factor_node = BooleanNode(True)
            else:
                self.__expect_and_consume(TokenType.FALSE)
                factor_node = BooleanNode(False)

        elif self.__expected_token(TokenType.LPAR):
            self.__expect_and_consume(TokenType.LPAR)
            factor_node = FactorNode(self.parse_expr())
            self.__expect_and_consume(TokenType.RPAR)

        elif self.__expected_token(TokenType.NOT):
            self.__consume_token()
            left_node = OperatorNode("not")
            right_node = self.parse_factor()
            factor_node = FactorNode(left_node, right_node)

        elif self.__expected_token(TokenType.NEG):
            self.__consume_token()
            left_node = OperatorNode("-")
            right_node = self.parse_factor()
            factor_node = FactorNode(left_node, right_node)

        else:
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[ID or INT or FLOAT or STR or TRUE or FALSE or LPAR or NOT or NEG]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        self.__log("</Factor>")
        return factor_node

    def parse_repl(self, repl_input: str) -> Node:
        """
        Entry point for the parser to parse a REPL input string
        and return the respective AST
        """
        self.__log("<Repl>")
        # Prepare lexer
        self.__lexer.analyze_repl(repl_input)
        self.__consume_token()

        if self.__expected_token(TokenType.DEF):
            repl_node = self.parse_func_def()
        elif TokenType.statement_start(self.curr_tkn):
            if TokenType.bin_op(self.__peek_token()):
                repl_node = self.parse_expr()
            else:
                repl_node = self.parse_body()
        elif TokenType.expression(self.curr_tkn):
            repl_node = self.parse_expr()
        else:
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[EXPR or STATEMENT_TYPE or DEFINE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        if self.curr_tkn.type != TokenType.ENDMARKER:
            raise ParserError(
                "Invalid syntax", self.curr_tkn.line_num, self.curr_tkn.column_num
            )

        self.__log("</Repl>")
        return repl_node

    def parse_source(self, filepath: str):
        """Entry point for the parser to parse a Nyaa source file"""
        source = Path(filepath)
        if source.exists():
            try:
                # Prepare lexer
                self.__lexer.analyze_src_file(source)
                self.__consume_token()

                self.__log("<Program>")
                ast = self.parse_program()
                self.__log("</Program>")
                return ast
            except ParserError as e:
                print(e, file=sys.stderr)
                exit(1)
            except LexerError as e:
                print(e, file=sys.stderr)
                exit(1)
        else:
            print(f"Error: '{source}' not found!", file=sys.stderr)
            exit(1)
