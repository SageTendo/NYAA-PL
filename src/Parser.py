from src.AST.AST import BodyNode, ReturnNode, PassNode, ProgramNode, SimpleExprNode, AssignmentNode, IdentifierNode, \
    PostfixExprNode, PrintNode, ArgsNode, NumericLiteralNode, StringLiteralNode, BooleanOpNode, NegationNode, \
    FactorNode, NotNode, TermNode, MulOpNode, AddOpNode, ExprNode, CallNode, InputNode, BreakNode, ContinueNode, \
    WhileNode, IfNode, ElifNode, TryCatchNode, FuncDefNode, RelOpNode
from src.Lexer import Lexer
from src.Types import TokenType
from src.utils.ErrorHandler import success_msg, warning_msg, throw_unexpected_token_err


class Parser:
    __debug_mode = False

    def __init__(self):
        self.curr_tkn = None
        self.__lexer = Lexer()
        self.__program_AST = None

    def debug_info(self, msg, success=True):
        """
        Print a debug message
        @param msg: The message to display
        @param success: Whether the message is a success message or not
        """
        if self.__debug_mode:
            success_msg(msg) if success else warning_msg(msg)

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

    def consume_token(self):
        """
        Consumes the current token and prepares the next token to be parsed
        """
        self.debug_info(f"Consuming {self.curr_tkn}...", success=False)
        self.curr_tkn = self.__lexer.get_token()

    def parse_program(self):
        """
        program: funcDef* MAIN LPAR RPAR TO (LBRACE body RBRACE | statement ';') | EOF;
        @return: The AST
        """
        program_node = ProgramNode()

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
            self.debug_info("<Statements>")
            program_node.set_body(self.parse_body())
            self.__expect_and_consume(TokenType.SEMICOLON)
        else:
            #  { body* }
            self.__expect_and_consume(TokenType.LBRACE)
            self.debug_info("<Statements>")
            program_node.set_body(self.parse_body())
            self.__expect_and_consume(TokenType.RBRACE)

        self.debug_info("</Statements>")
        return program_node

    def parse_body(self):
        """
        body:               statement*
        statement:          PASS | retStatement | assignmentStatement | whileStatement | ifStatement | printStatement
                            | inputStatement | callStatement | postfixStatement | tryCatchStatement
        @return: BodyNode
        """
        body = BodyNode()
        while TokenType.statement_start(self.curr_tkn):

            # Pass statement
            if self.match(TokenType.PASS):
                self.__expect_and_consume(TokenType.PASS)

                self.debug_info("<PASS>")
                body.append(PassNode())
                self.debug_info("</PASS>")

            #  Return statement
            elif self.match(TokenType.RET):
                self.debug_info("<Return>")
                body.append(self.parse_return())
                self.debug_info("</Return>")

            elif self.match(TokenType.ID):
                # assignment statement
                if self.peek_token().type == TokenType.ASSIGN:
                    self.debug_info("<Assignment>")
                    body.append(self.parse_assignment())
                    self.debug_info("</Assignment>")

                # postfix statement
                elif TokenType.postfix(self.peek_token()):
                    self.debug_info("<Postfix>")
                    body.append(self.parse_postfix())
                    self.debug_info("</Postfix>")

                # call (func calls) statement
                elif self.peek_token().type == TokenType.LPAR:
                    self.debug_info("<FuncCall>")
                    body.append(self.parse_func_call())
                    self.debug_info("</FuncCall>")

                else:
                    throw_unexpected_token_err(
                        self.curr_tkn.type,
                        "ASSIGNMENT_TYPE / POSTFIX_TYPE / FUNC_CALL_TYPE",
                        self.__lexer.get_line_number(),
                        self.__lexer.get_col_number())
            else:
                # while statement
                if self.match(TokenType.WHILE):
                    self.debug_info("<While>")
                    body.append(self.parse_while())
                    self.debug_info("</While>")

                # if statement
                elif self.match(TokenType.IF):
                    self.debug_info("<If>")
                    body.append(self.parse_if())
                    self.debug_info("</If>")

                # print statement
                elif self.match(TokenType.PRINT):
                    self.debug_info("<Print>")
                    body.append(self.parse_print())
                    self.debug_info("</Print>")

                # input statement
                elif self.match(TokenType.INPUT):
                    self.debug_info("<Input>")
                    body.append(self.parse_input())
                    self.debug_info("</Input>")

                # try-catch statement
                elif self.match(TokenType.TRY):
                    self.debug_info("<TryCatch>")
                    body.append(self.parse_try_catch())
                    self.debug_info("</TryCatch>")

        return body

    def parse_func_def(self):
        """
        FuncDef: DEF ID args TO (LBRACE body RBRACE | statement ';')
        @return: FuncDefNode
        """
        self.__expect_and_consume(TokenType.DEF)
        identifier = self.curr_tkn
        self.__expect_and_consume(TokenType.ID)

        args = None
        if self.peek_token().type == TokenType.RPAR:
            self.__expect_and_consume(TokenType.LPAR)
            self.__expect_and_consume(TokenType.RPAR)
        else:
            self.debug_info("<Args>")
            args = self.parse_args()
            self.debug_info("</Args>")

        self.__expect_and_consume(TokenType.TO)
        if TokenType.statement_start(self.curr_tkn):
            self.debug_info("<Statements>")
            body = self.parse_body()
            self.debug_info("</Statements>")
        else:
            self.__expect_and_consume(TokenType.LBRACE)
            self.debug_info("<Statements>")
            body = self.parse_body()
            self.debug_info("</Statements>")
            self.__expect_and_consume(TokenType.RBRACE)

        return FuncDefNode(identifier, args, body)

    def parse_func_call(self):
        """
        funcCall: ID args
        @return: CallNode
        """
        identifier = self.curr_tkn
        self.__expect_and_consume(TokenType.ID)

        self.debug_info("<Args>")
        args = self.parse_args()
        self.debug_info("</Args>")
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
        elif op == TokenType.UN_SUB:
            self.__expect_and_consume(TokenType.UN_SUB)

        return PostfixExprNode(left_node, op)

    def parse_assignment(self):
        """
        Assignment: ID ASSIGN (expr | callable)
        @return: AssignmentNode
        """
        left_node = IdentifierNode(self.curr_tkn)
        self.__expect_and_consume(TokenType.ID)

        self.__expect_and_consume(TokenType.ASSIGN)
        if TokenType.callable(self.curr_tkn) and self.peek_token().type == TokenType.LPAR:
            self.debug_info("<Callable>")
            right_node = self.parse_callable()
            self.debug_info("</Callable>")
        else:
            self.debug_info("<Expr>")
            right_node = self.parse_expr()
            self.debug_info("</Expr>")

        return AssignmentNode(left_node, right_node)

    def parse_while(self):
        """
        WhileStatement: WHILE ( expr ) { ( body | BREAK | CONTINUE) }
        @return: WhileNode
        """
        right_node = None
        self.__expect_and_consume(TokenType.WHILE)

        self.__expect_and_consume(TokenType.LPAR)
        self.debug_info("<Expr>")
        left_node = self.parse_expr()
        self.debug_info("</Expr>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if self.match(TokenType.BREAK):
            self.__expect_and_consume(TokenType.BREAK)

            self.debug_info("<Break>")
            right_node = BreakNode()
            self.debug_info("</Break>")
        elif self.match(TokenType.CONTINUE):
            self.__expect_and_consume(TokenType.CONTINUE)

            self.debug_info("<Continue>")
            right_node = ContinueNode()
            self.debug_info("</Continue>")
        elif TokenType.statement_start(self.curr_tkn):
            self.debug_info("<Body>")
            right_node = self.parse_body()
            self.debug_info("</Body>")
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
        self.debug_info("<Expr>")
        left_node = self.parse_expr()
        self.debug_info("</Expr>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.statement_start(self.curr_tkn):
            self.debug_info("<Body>")
            right_node = self.parse_body()
            self.debug_info("</Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        # Parse elif and else statements
        if_node = IfNode(left_node, right_node)
        while self.match(TokenType.ELIF):
            self.debug_info("<Elif>")
            if_node.append_else_if(self.parse_elif())
            self.debug_info("</Elif>")

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
        self.debug_info("<Expr>")
        left_node = self.parse_expr()
        self.debug_info("</Expr>")
        self.__expect_and_consume(TokenType.RPAR)

        self.__expect_and_consume(TokenType.LBRACE)
        if TokenType.statement_start(self.curr_tkn):
            self.debug_info("<Body>")
            right_node = self.parse_body()
            self.debug_info("</Body>")
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
        if TokenType.statement_start(self.curr_tkn):
            self.debug_info("<Body>")
            body = self.parse_body()
            self.debug_info("</Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        return body

    def parse_try_catch(self):
        """
        TryCatchStatement: TRY { body } CATCH { catchBody }
        @return: TryCatchNode
        """
        self.__expect_and_consume(TokenType.TRY)

        self.__expect_and_consume(TokenType.LBRACE)
        self.debug_info("<Body>")
        try_body = self.parse_body()
        self.debug_info("</Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        self.__expect_and_consume(TokenType.EXCEPT)
        self.__expect_and_consume(TokenType.LBRACE)
        self.debug_info("<Body>")
        catch_body = self.parse_body()
        self.debug_info("</Body>")
        self.__expect_and_consume(TokenType.RBRACE)

        return TryCatchNode(try_body, catch_body)

    def parse_return(self):
        """
        ReturnStatement: RETURN expr?
        @return: ReturnNode
        """
        self.__expect_and_consume(TokenType.RET)

        return_node = ReturnNode()
        if (TokenType.expression(self.curr_tkn)
                and self.peek_token().type not in [TokenType.ASSIGN, TokenType.LPAR]):
            self.debug_info("<Expr>")
            return_node.set_expr(self.parse_expr())
            self.debug_info("</Expr>")
        return return_node

    def parse_print(self):
        """
        PrintStatement: PRINT args
        @return: PrintNode
        """
        self.__expect_and_consume(TokenType.PRINT)

        self.debug_info("<Args>")
        args = self.parse_args()
        self.debug_info("</Args>")

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
            self.debug_info("<Arg>")
            args.append(self.parse_arg())
            self.debug_info("</Arg>")

            while self.match(TokenType.COMMA):
                self.__expect_and_consume(TokenType.COMMA)

                self.debug_info("<Arg>")
                args.append(self.parse_arg())
                self.debug_info("</Arg>")
        self.__expect_and_consume(TokenType.RPAR)

        return args

    def parse_arg(self):
        """
        arg: callable | expr
        @return: CallNode | ExprNode
        """
        if self.peek_token().type == TokenType.LPAR:
            self.debug_info("<Callable>")
            arg = self.parse_callable()
            self.debug_info("</Callable>")
        else:
            self.debug_info("<Expr>")
            arg = self.parse_expr()
            self.debug_info("</Expr>")
        return arg

    def parse_callable(self):
        """
        callable: PRINT | INPUT | ID args
        @return: PrintNode | InputNode | CallNode
        """
        call_node = None
        if self.match(TokenType.PRINT):
            self.debug_info("<Print>")
            call_node = self.parse_print()
            self.debug_info("</Print>")
        elif self.match(TokenType.INPUT):
            self.debug_info("<Input>")
            call_node = self.parse_input()
            self.debug_info("</Input>")
        elif self.match(TokenType.ID):
            self.debug_info("<FuncCall>")
            call_node = self.parse_func_call()
            self.debug_info("</FuncCall>")
        return call_node

    def parse_expr(self):
        """
        expr: simpleExpr (relationalOp simpleExpr)*
        @return: ExprNode
        """
        if not TokenType.expression(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "EXPRESSION_TYPE", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        self.debug_info("<SimpleExpr>")
        left = self.parse_simple_expr()
        self.debug_info("</SimpleExpr>")

        if TokenType.rel_op(self.curr_tkn):
            op = self.curr_tkn.type
            self.consume_token()

            self.debug_info("<SimpleExpr>")
            right = self.parse_simple_expr()
            self.debug_info("</SimpleExpr>")

            return ExprNode(left, RelOpNode(op), right)
        return ExprNode(left)

    def parse_simple_expr(self):
        """
        simpleExpr: term (addOp term)*
        @return: SimpleExprNode
        """
        simple_expr = SimpleExprNode()

        if not TokenType.term(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "SIMPLE_EXPR_TYPE", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        self.debug_info("<Term>")
        simple_expr.append(self.parse_term())
        self.debug_info("</Term>")

        while TokenType.add_op(self.curr_tkn):
            op = self.curr_tkn.type
            self.consume_token()

            self.debug_info("<Term>")
            right_node = self.parse_term()
            self.debug_info("</Term>")

            simple_expr.append(AddOpNode(op))
            simple_expr.append(right_node)
        return simple_expr

    def parse_term(self):
        """
        term: ID | INT | INT '.' INT | STR | TRUE | FALSE | LPAR expr RPAR | NOT factor | NEG factor
        @return: TermNode
        """
        term = TermNode()
        if not TokenType.factor(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "TERM_TYPE", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        self.debug_info("<Factor>")
        term.append(self.parse_factor())
        self.debug_info("</Factor>")

        while TokenType.mul_op(self.curr_tkn):
            op = self.curr_tkn.type
            self.consume_token()

            self.debug_info("<Factor>")
            right_node = self.parse_factor()
            self.debug_info("</Factor>")

            term.append(MulOpNode(op))
            term.append(right_node)
        return term

    def parse_factor(self):
        """
        factor: ID | INT | INT '.' INT | STR | TRUE | FALSE | LPAR expr RPAR | NOT factor | NEG factor
        @return: FactorNode
        """
        factor_node = None
        if not TokenType.factor(self.curr_tkn):
            throw_unexpected_token_err(
                self.curr_tkn.type, "FACTOR_TYPE", self.__lexer.get_line_number(),
                self.__lexer.get_col_number())

        if self.match(TokenType.ID):
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
            factor_node = FactorNode(BooleanOpNode(self.curr_tkn))
            if self.curr_tkn.type == TokenType.TRUE:
                self.__expect_and_consume(TokenType.TRUE)
            else:
                self.__expect_and_consume(TokenType.FALSE)

        elif self.match(TokenType.LPAR):
            self.__expect_and_consume(TokenType.LPAR)

            self.debug_info("<Expr>")
            factor_node = self.parse_expr()
            self.debug_info("</Expr>")
            self.__expect_and_consume(TokenType.RPAR)

        elif self.match(TokenType.NOT):
            self.__expect_and_consume(TokenType.NOT)

            left_node = NotNode()
            self.debug_info("<Factor>")
            right_node = self.parse_factor()
            self.debug_info("</Factor>")

            return FactorNode(left_node, right_node)
        elif self.match(TokenType.NEG):
            self.__expect_and_consume(TokenType.NEG)

            left_node = NegationNode()
            self.debug_info("<Factor>")
            right_node = self.parse_factor()
            self.debug_info("</Factor>")

            return FactorNode(left_node, right_node)
        return factor_node

    def parse(self, source_path, dflags):
        """
        Entry point for the parser
        @param source_path: The Nyaa source code
        @param dflags: Debug flags for the lexer and parser
        @return: The AST of the Nyaa source code
        """
        # Prepare lexer
        self.__lexer.load_src_file(source_path)
        self.__lexer.verbose(dflags.get("lexer", False))

        # Parse source code
        self.__debug_mode = dflags.get("parser", False)

        self.debug_info("<Program>")
        self.consume_token()
        ast = self.parse_program()
        self.debug_info("</Program>")

        return ast
