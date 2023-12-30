from src.Lexer import Lexer
from src.core.AComponent import AComponent
from src.core.ASTNodes import BodyNode, ReturnNode, PassNode, ProgramNode, SimpleExprNode, AssignmentNode, \
    IdentifierNode, \
    PostfixExprNode, PrintNode, ArgsNode, NumericLiteralNode, StringLiteralNode, BooleanNode, FactorNode, ExprNode, \
    CallNode, InputNode, BreakNode, ContinueNode, \
    WhileNode, IfNode, ElifNode, FuncDefNode, TermNode, OperatorNode
from src.core.Types import TokenType
from src.utils.ErrorHandler import success_msg, warning_msg, throw_unexpected_token_err


class Parser(AComponent):
    def __init__(self):
        super().__init__()

        self.curr_tkn = None
        self.__lexer = Lexer()
        self.__program_AST = None

    def debug(self, msg, success=True):
        """
        Print a debug message
        @param msg: The message to display
        @param success: Whether the message is a success message or not
        """
        message = success_msg(msg) if success else warning_msg(msg)
        super().debug(message)

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
                throw_unexpected_token_err(self.curr_tkn.type, expected_type, self.__lexer.get_line_number(),
                                           self.__lexer.get_col_number())

    def __expect_and_consume_op(self):
        """
        Check the current token is of an operator type. Consume the token if it matches, otherwise throw an error
        """
        if TokenType.bin_op(self.curr_tkn) or TokenType(self.curr_tkn.type):
            self.consume_token()
        else:
            throw_unexpected_token_err(self.curr_tkn.type, "[OPERATOR_TYPE]", self.__lexer.get_line_number(),
                                       self.__lexer.get_col_number())

    def consume_token(self):
        """
        Consumes the current token and prepares the next token to be parsed
        """
        self.debug(f"Consuming {self.curr_tkn}...", success=False)
        self.curr_tkn = self.__lexer.get_token()

    def handle_op_token(self):
        token_type = self.curr_tkn.type
        self.__expect_and_consume_op()

        if token_type == TokenType.PLUS:
            return '+'
        elif token_type == TokenType.MINUS:
            return '-'
        elif token_type == TokenType.NEG:
            return OperatorNode('-')
        elif token_type == TokenType.MULTIPLY:
            return '*'
        elif token_type == TokenType.DIVIDE:
            return '/'
        elif token_type == TokenType.AND:
            return 'and'
        elif token_type == TokenType.OR:
            return 'or'
        elif token_type == TokenType.NOT:
            return OperatorNode('not')
        elif token_type == TokenType.LT:
            return '<'
        elif token_type == TokenType.GT:
            return '>'
        elif token_type == TokenType.LTE:
            return '<='
        elif token_type == TokenType.GTE:
            return '>='
        elif token_type == TokenType.EQ:
            return '=='
        elif token_type == TokenType.NEQ:
            return '!='

    def parse_program(self):
        """
        program: funcDef* MAIN LPAR RPAR TO (LBRACE body RBRACE | statement ';') | EOF;
        @return: The AST
        """
        program_node = ProgramNode()
        program_node.start_pos = self.__lexer.get_col_number()

        if self.curr_tkn.type == TokenType.ENDMARKER:
            program_node.set_eof()
            return program_node

        # parse function definitions
        while self.curr_tkn.type == TokenType.DEF:
            program_node.append_func(self.parse_func_def())

        # handle uWu_nyaa() => { tokens
        self.__expect_and_consume(TokenType.MAIN)
        self.__expect_and_consume(TokenType.LPAR)
        self.__expect_and_consume(TokenType.RPAR)
        self.__expect_and_consume(TokenType.TO)

        # Parse single statement or multiple statements
        if TokenType.statement_start(self.curr_tkn):
            self.debug("<Statements>")
            program_node.set_body(self.parse_body())
            self.__expect_and_consume(TokenType.SEMICOLON)
        else:
            #  { body* }
            self.__expect_and_consume(TokenType.LBRACE)
            self.debug("<Statements>")
            program_node.set_body(self.parse_body())
            self.__expect_and_consume(TokenType.RBRACE)

        self.debug("</Statements>")

        program_node.end_pos = self.__lexer.get_col_number()
        return program_node

    def parse_body(self):
        """
        body:   statement*
        @return: BodyNode
        """
        body = BodyNode()
        while TokenType.statement_start(self.curr_tkn):
            body.append(self.parse_statement())
        return body

    def parse_conditional_body(self):
        """
        conditionalBody:    statement conditionalBody? | BREAK | CONTINUE
        @return: body
        """
        body = BodyNode()

        while TokenType.statement_start(self.curr_tkn):
            body.append(self.parse_statement())

        if self.match(TokenType.BREAK):
            self.__expect_and_consume(TokenType.BREAK)
            body.append(BreakNode())
        elif self.match(TokenType.CONTINUE):
            self.__expect_and_consume(TokenType.CONTINUE)
            body.append(ContinueNode())

        return body

    def parse_statement(self):
        """
        statement:  PASS | retStatement | assignmentStatement |
                    whileStatement | ifStatement | printStatement |
                    inputStatement | callStatement | postfixStatement
        @return: A statement node
        """
        statement_node = None

        # Pass statement
        if self.match(TokenType.PASS):
            self.__expect_and_consume(TokenType.PASS)

            self.debug("<PASS>")
            statement_node = PassNode()
            self.debug("</PASS>")

        #  Return statement
        elif self.match(TokenType.RET):
            self.debug("<Return>")
            statement_node = self.parse_return()
            self.debug("</Return>")

        elif self.match(TokenType.ID):
            # assignment statement
            if self.peek_token().type == TokenType.ASSIGN:
                self.debug("<Assignment>")
                statement_node = self.parse_assignment()
                self.debug("</Assignment>")

            # postfix statement
            elif TokenType.postfix(self.peek_token()):
                self.debug("<Postfix>")
                statement_node = self.parse_postfix()
                self.debug("</Postfix>")

            # call (func calls) statement
            elif self.peek_token().type == TokenType.LPAR:
                self.debug("<FuncCall>")
                statement_node = self.parse_func_call()
                self.debug("</FuncCall>")

            else:
                self.__expect_and_consume(TokenType.ID)
                throw_unexpected_token_err(
                    self.curr_tkn.type,
                    "[ASSIGNMENT_TYPE or POSTFIX_TYPE or FUNC_CALL_TYPE]",
                    self.__lexer.get_line_number(),
                    self.__lexer.get_col_number())
        else:
            # while statement
            if self.match(TokenType.WHILE):
                self.debug("<While>")
                statement_node = self.parse_while()
                self.debug("</While>")

            # if statement
            elif self.match(TokenType.IF):
                self.debug("<If>")
                statement_node = self.parse_if()
                self.debug("</If>")

            # print statement
            elif self.match(TokenType.PRINT):
                self.debug("<Print>")
                statement_node = self.parse_print()
                self.debug("</Print>")

            # input statement
            elif self.match(TokenType.INPUT):
                self.debug("<Input>")
                statement_node = self.parse_input()
                self.debug("</Input>")

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
            self.debug("<Args>")
            args = self.parse_args()
            self.debug("</Args>")

        self.__expect_and_consume(TokenType.TO)
        if TokenType.statement_start(self.curr_tkn):
            self.debug("<Statements>")
            body = self.parse_body()
            self.debug("</Statements>")
        else:
            self.__expect_and_consume(TokenType.LBRACE)
            self.debug("<Statements>")
            body = self.parse_body()
            self.debug("</Statements>")
            self.__expect_and_consume(TokenType.RBRACE)

        return FuncDefNode(identifier, args, body)

    def parse_func_call(self):
        """
        funcCall: ID args
        @return: CallNode
        """
        identifier = self.curr_tkn.value
        self.__expect_and_consume(TokenType.ID)

        self.debug("<Args>")
        args = self.parse_args()
        self.debug("</Args>")
        return CallNode(identifier, args)

    def parse_postfix(self):
        """
        PostfixExpr: ID (UN_ADD | UN_SUB)
        @return: PostfixExprNode
        """
        left_node = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)

        op = self.curr_tkn.type
        if op == TokenType.UN_ADD:
            self.__expect_and_consume(TokenType.UN_ADD)
            return PostfixExprNode(left_node, "++")
        elif op == TokenType.UN_SUB:
            self.__expect_and_consume(TokenType.UN_SUB)
            return PostfixExprNode(left_node, "--")

    def parse_assignment(self):
        """
        Assignment: ID ASSIGN (expr | callable)
        @return: AssignmentNode
        """
        left_node = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)

        self.__expect_and_consume(TokenType.ASSIGN)
        if TokenType.callable(self.curr_tkn) and self.peek_token().type == TokenType.LPAR:
            self.debug("<Callable>")
            right_node = self.parse_callable()
            self.debug("</Callable>")
        else:
            self.debug("<Expr>")
            right_node = self.parse_expr()
            self.debug("</Expr>")

        return AssignmentNode(left_node, right_node)

    def parse_while(self):
        """
        WhileStatement: WHILE ( expr ) { ( body | BREAK | CONTINUE) }
        @return: WhileNode
        """
        right_node = None
        self.__expect_and_consume(TokenType.WHILE)

        self.__expect_and_consume(TokenType.LPAR)
        self.debug("<Expr>")
        left_node = self.parse_expr()
        self.debug("</Expr>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            self.debug("<Cond Body>")
            right_node = self.parse_conditional_body()
            self.debug("</Cond Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        return WhileNode(left_node, right_node)

    def parse_if(self):
        """
        IfStatement: IF ( expr ) { body }
        @return: IfNode
        """
        right_node = None
        self.__expect_and_consume(TokenType.IF)

        self.__expect_and_consume(TokenType.LPAR)
        self.debug("<Expr>")
        left_node = self.parse_expr()
        self.debug("</Expr>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            self.debug("<Cond Body>")
            right_node = self.parse_conditional_body()
            self.debug("</Cond Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        # Parse elif and else statements
        if_node = IfNode(left_node, right_node)
        while self.match(TokenType.ELIF):
            self.debug("<Elif>")
            if_node.append_else_if(self.parse_elif())
            self.debug("</Elif>")

        if self.match(TokenType.ELSE):
            if_node.set_else_body(self.parse_else())
        return if_node

    def parse_elif(self):
        """
        ElifStatement: ELIF ( expr ) { body }
        @return: ElifNode
        """
        right_node = None
        self.__expect_and_consume(TokenType.ELIF)

        self.__expect_and_consume(TokenType.LPAR)
        self.debug("<Expr>")
        left_node = self.parse_expr()
        self.debug("</Expr>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            self.debug("<Cond Body>")
            right_node = self.parse_conditional_body()
            self.debug("</Cond Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        return ElifNode(left_node, right_node)

    def parse_else(self):
        """
        ElseStatement: ELSE { body }
        @return: BodyNode
        """
        body = None
        self.__expect_and_consume(TokenType.ELSE)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.conditional_stmt_start(self.curr_tkn):
            self.debug("<Cond Body>")
            body = self.parse_conditional_body()
            self.debug("</Cond Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        return body

    def parse_return(self):
        """
        ReturnStatement: RETURN expr?
        @return: ReturnNode
        """
        self.__expect_and_consume(TokenType.RET)

        return_node = ReturnNode()
        if (TokenType.expression(self.curr_tkn) and
                self.peek_token().type != TokenType.ASSIGN):
            self.debug("<Expr>")
            return_node.set_expr(self.parse_expr())
            self.debug("</Expr>")
        return return_node

    def parse_print(self):
        """
        PrintStatement: PRINT args
        @return: PrintNode
        """
        self.__expect_and_consume(TokenType.PRINT)

        self.debug("<Args>")
        args = self.parse_args()
        self.debug("</Args>")

        return PrintNode(args)

    def parse_input(self):
        """
        InputStatement: INPUT (STR)?
        @return: InputNode
        """
        self.__expect_and_consume(TokenType.INPUT)
        self.__expect_and_consume(TokenType.LPAR)

        msg = None
        if self.match(TokenType.STR):
            msg = self.curr_tkn.value
            self.__expect_and_consume(TokenType.STR)
        self.__expect_and_consume(TokenType.RPAR)
        return InputNode(msg)

    def parse_args(self):
        """
        args: arg (',' arg)*
        @return: ArgsNode
        """
        args = ArgsNode()

        self.__expect_and_consume(TokenType.LPAR)
        if TokenType.expression(self.curr_tkn) or TokenType.callable(self.curr_tkn):
            self.debug("<Arg>")
            args.append(self.parse_arg())
            self.debug("</Arg>")

            while self.match(TokenType.COMMA):
                self.__expect_and_consume(TokenType.COMMA)

                self.debug("<Arg>")
                args.append(self.parse_arg())
                self.debug("</Arg>")
        self.__expect_and_consume(TokenType.RPAR)

        return args

    def parse_arg(self):
        """
        arg: callable | expr
        @return: CallNode | ExprNode
        """
        if self.peek_token().type == TokenType.LPAR:
            self.debug("<Callable>")
            arg = self.parse_callable()
            self.debug("</Callable>")
        else:
            self.debug("<Expr>")
            arg = self.parse_expr()
            self.debug("</Expr>")
        return arg

    def parse_callable(self):
        """
        callable: PRINT | INPUT | ID args
        @return: PrintNode | InputNode | CallNode
        """
        call_node = None
        if self.match(TokenType.PRINT):
            self.debug("<Print>")
            call_node = self.parse_print()
            self.debug("</Print>")
        elif self.match(TokenType.INPUT):
            self.debug("<Input>")
            call_node = self.parse_input()
            self.debug("</Input>")
        elif self.match(TokenType.ID):
            self.debug("<FuncCall>")
            call_node = self.parse_func_call()
            self.debug("</FuncCall>")
        return call_node

    def parse_expr(self):
        """
        expr: simpleExpr | simpleExpr relationalOp expr
        @return: ExprNode
        """
        expr_node = ExprNode()

        if not TokenType.expression(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "[EXPRESSION_TYPE]", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        self.debug("<SimpleExpr>")
        expr_node.left = self.parse_simple_expr()
        self.debug("</SimpleExpr>")

        if TokenType.rel_op(self.curr_tkn):
            expr_node.op = self.handle_op_token()

            self.debug("<Expr>")
            expr_node.right = self.parse_expr()
            self.debug("</Expr>")

        return expr_node

    def parse_simple_expr(self):
        """
        simpleExpr: term | term addOp simpleExpr
        @return: SimpleExprNode
        """
        simple_expr = SimpleExprNode()

        if not TokenType.term(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "[SIMPLE_EXPR_TYPE]", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        self.debug("<Term>")
        simple_expr.left = self.parse_term()
        self.debug("</Term>")

        if TokenType.add_op(self.curr_tkn):
            simple_expr.op = self.handle_op_token()

            self.debug("<SimpleExpr>")
            simple_expr.right = self.parse_simple_expr()
            self.debug("</SimpleExpr>")

        return simple_expr

    def parse_term(self):
        """
        term: factor | factor mulOp term
        @return: TermNode
        """
        term = TermNode()
        if not TokenType.factor(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "[TERM_TYPE]", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        self.debug("<Factor>")
        term.left = self.parse_factor()
        self.debug("</Factor>")

        if TokenType.mul_op(self.curr_tkn):
            term.op = self.handle_op_token()

            self.debug("<Term>")
            term.right = self.parse_term()
            self.debug("</Term>")

        return term

    def parse_factor(self):
        """
        factor: ID | INT | INT '.' INT | STR | TRUE | FALSE | LPAR expr RPAR | NOT factor | NEG factor | Func_Call
        @return: FactorNode
        """
        factor_node = None
        if not TokenType.factor(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "[FACTOR_TYPE]", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        if self.match(TokenType.ID):

            # Check if it is a function call
            if self.peek_token().type == TokenType.LPAR:
                factor_node = self.parse_func_call()
            else:
                # Check if it is an identifier
                factor_node = FactorNode(IdentifierNode(self.curr_tkn))
                self.__expect_and_consume(TokenType.ID)

        elif self.match(TokenType.INT) or self.match(TokenType.FLOAT):
            factor_node = FactorNode(NumericLiteralNode(self.curr_tkn))
            if self.curr_tkn.type == TokenType.INT:
                self.__expect_and_consume(TokenType.INT)
            else:
                self.__expect_and_consume(TokenType.FLOAT)

        elif self.match(TokenType.STR):
            factor_node = FactorNode(StringLiteralNode(self.curr_tkn))
            self.__expect_and_consume(TokenType.STR)

        elif self.match(TokenType.TRUE) or self.match(TokenType.FALSE):

            if self.curr_tkn.type == TokenType.TRUE:
                self.__expect_and_consume(TokenType.TRUE)
                factor_node = FactorNode(BooleanNode(True))
            else:
                self.__expect_and_consume(TokenType.FALSE)
                factor_node = FactorNode(BooleanNode(False))

        elif self.match(TokenType.LPAR):
            self.__expect_and_consume(TokenType.LPAR)

            self.debug("<Expr>")
            factor_node = self.parse_expr()
            self.debug("</Expr>")
            self.__expect_and_consume(TokenType.RPAR)

        elif self.match(TokenType.NOT):

            left_node = self.handle_op_token()
            self.debug("<Factor>")
            right_node = self.parse_factor()
            self.debug("</Factor>")

            return FactorNode(left_node, right_node)
        elif self.match(TokenType.NEG):

            left_node = self.handle_op_token()
            self.debug("<Factor>")
            right_node = self.parse_factor()
            self.debug("</Factor>")

            return FactorNode(left_node, right_node)
        return factor_node

    def parse_repl(self):
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
            throw_unexpected_token_err(self.curr_tkn.type, "[EXPR or STATEMENT_TYPE or DEFINE]",
                                       self.__lexer.get_line_number(), self.__lexer.get_col_number())

    def parse_source(self, source_path=None, repl_input=None, dflags=None):
        """
        Entry point for the parser
        @param repl_input: The REPL input
        @param source_path: The Nyaa source code
        @param dflags: Debug flags for the lexer and parser
        @return: The AST of the Nyaa source code
        """
        if dflags is None:
            dflags = {}

        lexer_flag = dflags.get("lexer", False)
        self.__lexer.verbose(lexer_flag)

        parser_flag = dflags.get("parser", False)
        self.verbose(parser_flag)

        # Prepare lexer
        if source_path:
            self.__lexer.analyze_src_file(source_path)
            self.consume_token()

            # Parse source code
            self.debug("<Program>")
            ast = self.parse_program()
            self.debug("</Program>")
            return ast
        elif repl_input:
            self.__lexer.analyze_repl(repl_input)
            self.consume_token()

            # Parse REPL input
            self.debug("<Repl>")
            repl_node = self.parse_repl()
            self.debug("</Repl>")
            return repl_node
        else:
            raise Exception("Either source_path or repl_input must be provided")
