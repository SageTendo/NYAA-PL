import sys

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
    def __init__(self, *, lexer, verbose=False):
        self.curr_tkn = Token()
        self.__lexer = lexer
        self.__program_AST = None
        self.__verbose = verbose

    def __log(self, msg, success=True):
        """
        Log a message to the console
        @param msg: The message to display
        @param success: Whether the message is a success message or not
        """
        if not self.__verbose:
            return

        message = success_msg(msg) if success else warning_msg(msg)
        print(message)

    def match(self, expected_type):
        """
        Check if the current token type matches the expected type
        @param expected_type: The type of token expected to be parsed
        @return: True if the current token type matches the expected type, False otherwise
        """
        return self.curr_tkn.type == expected_type

    def peek_token(self):
        """
        Peek at the next token to be parsed
        @return: The next token to be parsed
        """
        return self.__lexer.peek_token()

    def __expect_and_consume(self, expected_type):
        """
        Check the current token type matches the expected type. Consume the token if it matches,
        otherwise report an error
        @param expected_type: The type of token expected to be parsed
        """
        if self.match(expected_type):
            self.consume_token()
        else:
            if self.curr_tkn != expected_type:
                throw_unexpected_token_err(
                    self.curr_tkn.type,
                    expected_type,
                    self.curr_tkn.line_num,
                    self.curr_tkn.column_num,
                )

    def __expect_and_consume_op(self):
        """
        Check the current token is of an operator type. Consume the token if it matches, otherwise throw an error
        """
        if TokenType.bin_op(self.curr_tkn) or TokenType(self.curr_tkn.type):
            self.consume_token()
        else:
            throw_unexpected_token_err(
                self.curr_tkn.type,
                "[OPERATOR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

    def consume_token(self):
        """
        Consumes the current token and prepares the next token to be parsed
        """
        self.__log(f"Consuming {self.curr_tkn}...", success=False)
        self.curr_tkn = self.__lexer.get_token()

    def handle_op_token(self):
        token_type = self.curr_tkn.type
        self.__expect_and_consume_op()

        if token_type == TokenType.PLUS:
            return "+"
        elif token_type == TokenType.MINUS:
            return "-"
        elif token_type == TokenType.NEG:
            return OperatorNode("-")
        elif token_type == TokenType.MULTIPLY:
            return "*"
        elif token_type == TokenType.DIVIDE:
            return "/"
        elif token_type == TokenType.AND:
            return "and"
        elif token_type == TokenType.OR:
            return "or"
        elif token_type == TokenType.NOT:
            return OperatorNode("not")
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

    def parse_program(self):
        """
        program: funcDef* MAIN LPAR RPAR TO (LBRACE body RBRACE | statement ';') | EOF;
        @return: The AST
        """
        program_node = ProgramNode()
        program_node.start_pos = self.curr_tkn.pos

        if self.curr_tkn.type == TokenType.ENDMARKER:
            program_node.set_eof()
            program_node.end_pos = self.curr_tkn.pos
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
        program_node.end_pos = self.curr_tkn.pos
        return program_node

    def parse_body(self):
        """
        body:   statement*
        @return: BodyNode
        """
        self.__log("<Body>")

        body = BodyNode()
        start_pos = self.curr_tkn.pos
        while TokenType.statement_start(self.curr_tkn):
            body.append(self.parse_statement())

        self.__log("</Body>")
        body.start_pos = start_pos
        body.end_pos = self.curr_tkn.pos
        return body

    def parse_conditional_body(self):
        """
        conditionalBody:    statement conditionalBody? | BREAK | CONTINUE
        @return: body
        """
        self.__log("<ConditionalBody>")
        body = BodyNode()
        body.start_pos = self.curr_tkn.pos

        while TokenType.statement_start(self.curr_tkn):
            body.append(self.parse_statement())

        if self.match(TokenType.BREAK):
            self.__expect_and_consume(TokenType.BREAK)
            body.append(BreakNode())
        elif self.match(TokenType.CONTINUE):
            self.__expect_and_consume(TokenType.CONTINUE)
            body.append(ContinueNode())

        self.__log("</ConditionalBody>")
        body.end_pos = self.curr_tkn.pos
        return body

    def parse_statement(self):
        """
        statement:  PASS | retStatement | assignmentStatement |
                    whileStatement | ifStatement | printStatement |
                    inputStatement | callStatement | postfixStatement
        @return: A statement node
        """
        statement_node = None
        start_pos = self.curr_tkn.pos

        if self.match(TokenType.RET):
            statement_node = self.parse_return()

        elif self.match(TokenType.ID):
            if self.peek_token().type == TokenType.ASSIGN:
                statement_node = self.parse_assignment()

            elif TokenType.postfix(self.peek_token()):
                statement_node = self.parse_postfix()

            elif self.peek_token().type == TokenType.LPAR:
                statement_node = self.parse_func_call()

            elif self.peek_token().type == TokenType.TO:
                statement_node = self.parse_array_def()

            elif self.peek_token().type == TokenType.LBRACKET:
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
            if self.match(TokenType.WHILE):
                statement_node = self.parse_while()
            elif self.match(TokenType.FOR):
                statement_node = self.parse_for()
            elif self.match(TokenType.IF):
                statement_node = self.parse_if()
            elif self.match(TokenType.PRINT):
                statement_node = self.parse_print()
            elif self.match(TokenType.PRINTLN):
                statement_node = self.parse_print(print_ln=True)
            elif self.match(TokenType.INPUT):
                statement_node = self.parse_input()
            else:
                return throw_unexpected_token_err(
                    self.curr_tkn.type,
                    "[STATEMENT_TYPE]",
                    self.curr_tkn.line_num,
                    self.curr_tkn.column_num,
                )

        statement_node.start_pos = start_pos
        statement_node.end_pos = self.curr_tkn.pos
        return statement_node

    def parse_func_def(self):
        """
        FuncDef: DEF ID args TO (LBRACE body RBRACE | statement ';')
        @return: FuncDefNode
        """
        self.__expect_and_consume(TokenType.DEF)
        identifier = self.curr_tkn.value
        self.__expect_and_consume(TokenType.ID)

        args = None
        if self.peek_token().type == TokenType.RPAR:
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

        return FuncDefNode(identifier, args, body)

    def parse_func_call(self):
        """
        funcCall: ID args
        @return: CallNode
        """
        self.__log("<FuncCall>")

        identifier = self.curr_tkn.value
        start_pos = self.curr_tkn.pos
        self.__expect_and_consume(TokenType.ID)
        args = self.parse_args()

        self.__log("</FuncCall>")
        call_node = CallNode(identifier, args)
        call_node.start_pos = start_pos
        call_node.end_pos = self.curr_tkn.pos
        return call_node

    def parse_postfix(self):
        """
        PostfixExpr: ID (UN_ADD | UN_SUB)
        @return: PostfixExprNode
        """
        self.__log("<Postfix>")

        postfix_node = None
        start_pos = self.curr_tkn.pos
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
        postfix_node.end_pos = self.curr_tkn.pos
        return postfix_node

    def parse_index(self):
        """
        Index: [ simple_expr ]
        @return: SimpleExprNode
        """
        self.__log("<Index>")

        self.__expect_and_consume(TokenType.LBRACKET)
        simple_expr = self.parse_simple_expr()
        self.__expect_and_consume(TokenType.RBRACKET)

        self.__log("</Index>")
        return simple_expr

    def parse_array_def(self):
        """
        ArrayDef: ID => [ expr ] | { values* }
        @return:
        """
        self.__log("<ArrDef>")

        identifier = self.curr_tkn.value
        size = None
        values = []
        self.__expect_and_consume(TokenType.ID)
        self.__expect_and_consume(TokenType.TO)

        if self.match(TokenType.LBRACKET):
            self.__expect_and_consume(TokenType.LBRACKET)
            size = self.parse_simple_expr()
            self.__expect_and_consume(TokenType.RBRACKET)

        elif self.match(TokenType.LBRACE):
            self.__expect_and_consume(TokenType.LBRACE)
            while not self.match(TokenType.RBRACE):
                values.append(self.parse_expr())
                if self.match(TokenType.COMMA):
                    self.__expect_and_consume(TokenType.COMMA)
            self.__expect_and_consume(TokenType.RBRACE)

        self.__log("<ArrDef>")
        return ArrayNode(
            label="array_def", identifier=identifier, size=size, initial_values=values
        )

    def parse_array_access(self):
        """
        ArrayAccess: ID index
        @return:
        """
        self.__log("<ArrayAccess>")

        identifier = self.curr_tkn.value
        self.__expect_and_consume(TokenType.ID)
        index = self.parse_index()

        self.__log("</ArrayAccess>")
        return ArrayNode(label="array_access", identifier=identifier, index=index)

    def parse_array_assignment(self):
        """
        ArrayAssignment: ID index ASSIGN expr
        """
        self.__log("<ArrayAssign>")

        identifier = self.curr_tkn.value
        self.__expect_and_consume(TokenType.ID)
        index = self.parse_index()
        self.__expect_and_consume(TokenType.ASSIGN)
        expression = self.parse_expr()

        self.__log("</ArrayAssign>")
        return ArrayNode(
            label="array_update", identifier=identifier, index=index, value=expression
        )

    def parse_assignment(self):
        """
        Assignment: ID ASSIGN (expr | callable)
        @return: AssignmentNode
        """
        self.__log("<Assignment>")

        start_pos = self.curr_tkn.pos
        left_node = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)

        self.__expect_and_consume(TokenType.ASSIGN)
        if (
            TokenType.callable(self.curr_tkn)
            and self.peek_token().type == TokenType.LPAR
        ):
            right_node = self.parse_callable()
        else:
            right_node = self.parse_expr()

        self.__log("<Assignment>")
        assignment_node = AssignmentNode(left_node, right_node)
        assignment_node.start_pos = start_pos
        assignment_node.end_pos = self.curr_tkn.pos
        return assignment_node

    def parse_while(self):
        """
        WhileStatement: WHILE ( expr ) { ( body | BREAK | CONTINUE) }
        @return: WhileNode
        """
        self.__log("<While>")

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
        return WhileNode(left_node, right_node)

    def parse_for(self):
        """
        ForStatement: FOR ID TO ( NUM, NUM ) { body }
        @return: ForNode
        """
        self.__log("<For>")

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
        return ForNode(identifier, range_start, range_end, body)

    def parse_if(self):
        """
        IfStatement: IF ( expr ) { body }
        @return: IfNode
        """
        self.__log("<If>")

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
        while self.match(TokenType.ELIF):
            if_node.append_else_if(self.parse_elif())

        if self.match(TokenType.ELSE):
            if_node.set_else_body(self.parse_else())

        self.__log("</If>")
        return if_node

    def parse_elif(self):
        """
        ElifStatement: ELIF ( expr ) { body }
        @return: ElifNode
        """
        self.__log("<Elif>")
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
        return ElifNode(expr_node, body_node)

    def parse_else(self):
        """
        ElseStatement: ELSE { body }
        @return: BodyNode
        """
        self.__log("<Else>")

        body = None
        self.__expect_and_consume(TokenType.ELSE)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            body = self.parse_conditional_body()
        self.__expect_and_consume(TokenType.RBRACE)

        self.__log("</Else>")
        return body

    def parse_return(self):
        """
        ReturnStatement: RETURN expr?
        @return: ReturnNode
        """
        self.__log("<Return>")

        start_pos = self.curr_tkn.pos
        self.__expect_and_consume(TokenType.RET)

        return_node = ReturnNode()
        if (
            TokenType.expression(self.curr_tkn)
            and self.peek_token().type != TokenType.ASSIGN
        ):
            return_node.set_expr(self.parse_expr())

        self.__log("</Return>")
        return_node.start_pos = start_pos
        return_node.end_pos = self.curr_tkn.pos
        return return_node

    def parse_print(self, print_ln=False):
        """
        PrintStatement: PRINT args
        @return: PrintNode
        """
        self.__log("<Print>")

        start_pos = self.curr_tkn.pos

        # PrintlnStatement: PRINTLN args
        if self.curr_tkn.type == TokenType.PRINTLN:
            self.__expect_and_consume(TokenType.PRINTLN)
        else:
            self.__expect_and_consume(TokenType.PRINT)

        args = self.parse_args()
        print_node = PrintNode(args, print_ln)

        self.__log("</Print>")
        print_node.start_pos = start_pos
        print_node.end_pos = self.curr_tkn.pos
        return print_node

    def parse_input(self):
        """
        InputStatement: INPUT (STR)?
        @return: InputNode
        """
        self.__log("<Input>")

        start_pos = self.curr_tkn.pos
        self.__expect_and_consume(TokenType.INPUT)
        self.__expect_and_consume(TokenType.LPAR)

        msg = None
        if self.match(TokenType.STR):
            msg = self.curr_tkn.value
            self.__expect_and_consume(TokenType.STR)
        self.__expect_and_consume(TokenType.RPAR)
        input_node = InputNode(msg)

        self.__log("</Input>")
        input_node.start_pos = start_pos
        input_node.end_pos = self.curr_tkn.pos
        return input_node

    def parse_params(self):
        """
        params: param (',' param)*
        @return: ArgsNode
        """
        self.__log("<Params>")

        params = ArgsNode()
        params.start_pos = self.curr_tkn.pos

        self.__expect_and_consume(TokenType.LPAR)
        if not (self.match(TokenType.ID) or self.match(TokenType.RPAR)):
            throw_unexpected_token_err(
                self.curr_tkn.type,
                "[ID or RPAR]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        if self.match(TokenType.ID):
            self.__log("<Param>")
            params.append(IdentifierNode(self.curr_tkn))
            self.__expect_and_consume(TokenType.ID)
            self.__log("</Param>")

            while self.match(TokenType.COMMA):
                self.__expect_and_consume(TokenType.COMMA)

                self.__log("<Param>")
                params.append(IdentifierNode(self.curr_tkn))
                self.__expect_and_consume(TokenType.ID)
                self.__log("</Param>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__log("</Params>")
        params.end_pos = self.curr_tkn.pos
        return params

    def parse_args(self):
        """
        args: arg (',' arg)*
        @return: ArgsNode
        """
        self.__log("<Args>")

        args = ArgsNode()
        args.start_pos = self.curr_tkn.pos

        self.__expect_and_consume(TokenType.LPAR)
        if TokenType.expression(self.curr_tkn) or TokenType.callable(self.curr_tkn):
            args.append(self.parse_arg())

            while self.match(TokenType.COMMA):
                self.__expect_and_consume(TokenType.COMMA)
                args.append(self.parse_arg())
        self.__expect_and_consume(TokenType.RPAR)

        self.__log("</Args>")
        args.end_pos = self.curr_tkn.pos
        return args

    def parse_arg(self):
        """
        arg: callable | expr
        @return: CallNode | ExprNode
        """
        self.__log("<Arg>")

        if self.peek_token().type == TokenType.LPAR:
            arg = self.parse_callable()
        else:
            arg = self.parse_expr()

        self.__log("</Arg>")
        return arg

    def parse_callable(self):
        """
        callable: PRINT | INPUT | ID args
        @return: PrintNode | InputNode | CallNode
        """
        self.__log("<Callable>")

        call_node = None
        start_pos = self.curr_tkn.pos

        if self.match(TokenType.PRINT):
            call_node = self.parse_print()
        elif self.match(TokenType.INPUT):
            call_node = self.parse_input()
        elif self.match(TokenType.ID):
            call_node = self.parse_func_call()
        else:
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "CALLABLE_TYPE",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        self.__log("</Callable>")
        call_node.start_pos = start_pos
        call_node.end_pos = self.curr_tkn.pos
        return call_node

    def parse_expr(self):
        """
        expr: simpleExpr | simpleExpr relationalOp simpleExpr
        @return: ExprNode
        """
        self.__log("<Expr>")

        expr_node = ExprNode()
        expr_node.start_pos = self.curr_tkn.pos

        if not TokenType.expression(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[EXPRESSION_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        expr_node.left = self.parse_simple_expr()
        if TokenType.rel_op(self.curr_tkn):
            expr_node.operator = self.handle_op_token()
            expr_node.right = self.parse_expr()

        expr_node.end_pos = self.curr_tkn.pos
        self.__log("</Expr>")
        return expr_node

    def parse_simple_expr(self):
        """
        simpleExpr: term | term addOp simpleExpr
        @return: SimpleExprNode
        """
        self.__log("<SimpleExpr>")

        start_pos = self.curr_tkn.pos
        if not TokenType.term(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[SIMPLE_EXPR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        left = self.parse_term()
        while TokenType.add_op(self.curr_tkn):
            op = self.handle_op_token()
            right = self.parse_term()
            left = SimpleExprNode(left, right, op)

        self.__log("</SimpleExpr>")
        left.start_pos = start_pos
        left.end_pos = self.curr_tkn.pos
        return left

    def parse_term(self):
        """
        term: factor | factor mulOp term
        @return: TermNode
        """
        self.__log("<Term>")

        start_pos = self.curr_tkn.pos
        if not TokenType.factor(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[TERM_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        left = self.parse_factor()
        while TokenType.mul_op(self.curr_tkn):
            op = self.handle_op_token()
            right = self.parse_factor()
            left = TermNode(left, right, op)

        self.__log("</Term>")
        left.start_pos = start_pos
        left.end_pos = self.curr_tkn.pos
        return left

    def parse_factor(self):
        """
        factor: ID | INT | INT '.' INT | STR | TRUE | FALSE | LPAR expr RPAR | NOT factor | NEG factor | Func_Call
        @return: FactorNode
        """
        self.__log("<Factor>")

        factor_node = None
        if not TokenType.factor(self.curr_tkn):
            return throw_unexpected_token_err(
                self.curr_tkn.type,
                "[FACTOR_TYPE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

        if self.match(TokenType.ID):

            if self.peek_token().type == TokenType.LPAR:
                factor_node = self.parse_func_call()

            elif self.peek_token().type == TokenType.LBRACKET:
                start_pos = self.curr_tkn.pos
                array_access_node = self.parse_array_access()
                array_access_node.start_pos = start_pos
                array_access_node.end_pos = self.curr_tkn.pos
                factor_node = FactorNode(array_access_node)

            else:
                factor_node = IdentifierNode(self.curr_tkn)
                self.__expect_and_consume(TokenType.ID)

        elif self.match(TokenType.INT) or self.match(TokenType.FLOAT):
            factor_node = NumericLiteralNode(self.curr_tkn)
            if self.curr_tkn.type == TokenType.INT:
                self.__expect_and_consume(TokenType.INT)
            else:
                self.__expect_and_consume(TokenType.FLOAT)

        elif self.match(TokenType.STR):
            factor_node = StringLiteralNode(self.curr_tkn)
            self.__expect_and_consume(TokenType.STR)

        elif self.match(TokenType.TRUE) or self.match(TokenType.FALSE):

            if self.curr_tkn.type == TokenType.TRUE:
                self.__expect_and_consume(TokenType.TRUE)
                factor_node = BooleanNode(True)
            else:
                self.__expect_and_consume(TokenType.FALSE)
                factor_node = BooleanNode(False)

        elif self.match(TokenType.LPAR):
            self.__expect_and_consume(TokenType.LPAR)
            factor_node = self.parse_expr()
            self.__expect_and_consume(TokenType.RPAR)

        elif self.match(TokenType.NOT):
            left_node = self.handle_op_token()
            right_node = self.parse_factor()
            factor_node = FactorNode(left_node, right_node)

        elif self.match(TokenType.NEG):
            left_node = self.handle_op_token()
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

    def parse_repl(self):
        """
        Parse REPL input and return the AST representation of the input
        @return: The AST representation of the REPL input
        """
        if self.match(TokenType.ENDMARKER):
            return None
        elif self.match(TokenType.DEF):
            return self.parse_func_def()
        elif TokenType.statement_start(self.curr_tkn):
            if TokenType.bin_op(self.peek_token()):
                return self.parse_expr()
            return self.parse_body()

        elif TokenType.expression(self.curr_tkn):
            return self.parse_expr()
        else:
            throw_unexpected_token_err(
                self.curr_tkn.type,
                "[EXPR or STATEMENT_TYPE or DEFINE]",
                self.curr_tkn.line_num,
                self.curr_tkn.column_num,
            )

    def parse_source(self, source_path=None, repl_input=None):
        """
        Entry point for the parser
        @param repl_input: The REPL input
        @param source_path: The Nyaa source code
        @return: The AST of the Nyaa source code
        """
        if source_path:
            try:
                # Prepare lexer
                self.__lexer.analyze_src_file(source_path)
                self.consume_token()

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

        elif repl_input:
            # Prepare lexer
            self.__lexer.analyze_repl(repl_input)
            self.consume_token()

            self.__log("<Repl>")
            repl_node = self.parse_repl()
            self.__log("</Repl>")
            return repl_node
        else:
            raise Exception("Either source_path or repl_input must be provided")
