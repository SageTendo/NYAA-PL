from pathlib import Path
from src.core.Token import Token, Position
from src.core.Types import TokenType
from src.utils.Constants import EOF, MAX_ID_LEN, MAX_STR_LEN
from src.utils.ErrorHandler import LexerError

RESERVED_WORDS = {
    "uWu_nyaa": TokenType.MAIN,
    "yomu": TokenType.PRINT,
    "ohayo": TokenType.INPUT,
    "daijoubu": TokenType.WHILE,
    "nani": TokenType.IF,
    "nandesuka": TokenType.ELIF,
    "baka": TokenType.ELSE,
    "yamete": TokenType.BREAK,
    "motto": TokenType.CONTINUE,
    "kawaii": TokenType.DEF,
    "HAI": TokenType.TRUE,
    "IIE": TokenType.FALSE,
    "modoru": TokenType.RET,
    "for": TokenType.FOR,
    "yomu_ln": TokenType.PRINTLN,
    "f_open": TokenType.FILE_OPEN,
    "f_close": TokenType.FILE_CLOSE,
    "f_read": TokenType.FILE_READ,
    "f_readline": TokenType.FILE_READLINE,
    "f_write": TokenType.FILE_WRITE,
    "f_writeline": TokenType.FILE_WRITELINE,
    "f_EOF": TokenType.FILE_EOF,  # TODO: Is this being used?
    "asChar": TokenType.GET_CHAR,
    "asInt": TokenType.GET_INT,
    "split": TokenType.STR_SPLIT,
    "len": TokenType.LEN,
}


class Lexer:
    """Represents a Lexer that tokenizes the source code"""

    def __init__(self, verbose: bool = False) -> None:
        """
        Initializes the Lexer
        @param verbose: Flag to enable logging
        """
        self.__char = ""
        self.__last_read_char = ""
        self.__line_number = 1
        self.__column_number = 0
        self.__token_position = Position(
            line=self.__line_number, col=self.__column_number
        )

        self.__program_buffer: list[str] = []
        self.__token_buffer: list[Token] = []
        self.__verbose = verbose

    def init(self) -> None:
        self.__init__(self.__verbose)

    def __next_char(self) -> None:
        """Get the next character from the program file"""
        if self.__last_read_char == "\n":
            self.__line_number += 1
            self.__column_number = 0

        if len(self.__program_buffer) == 0:
            self.__char = EOF
            return

        self.__char = self.__program_buffer.pop(0)
        self.__last_read_char = self.__char
        self.__column_number += 1

    def analyze_src_file(self, source_file: Path) -> None:
        """Reads in the source file for tokenization"""
        with open(source_file, "r") as source:
            c = source.read(1)
            while c:
                self.__program_buffer.append(c)
                c = source.read(1)
        self.__next_char()

    def analyze_repl(self, repl_input: str) -> None:
        """Reads in the REPL input for tokenization"""
        self.init()
        self.__program_buffer = list(repl_input)
        self.__next_char()

    def peek_token(self) -> Token:
        """Looks ahead at the next token to be processed (used during parsing)"""
        token = self.get_token()
        self.__token_buffer.append(token)
        return token

    def get_token(self) -> Token:
        """
        Scans through the source until a recognized symbol or
        keyword is found and returns it as a token object.
        """
        if len(self.__token_buffer) > 0:
            return self.__token_buffer.pop(0)

        token = Token()
        while self.__char.isspace():
            self.__next_char()

        self.__token_position = Position(
            line=self.__line_number, col=self.__column_number
        )

        if self.__char != EOF:
            if self.__char.isalpha() or self.__char == "_":
                self.__process_word(token)
            elif self.__char.isdigit():
                self.__process_number(token)

                if self.__char == ".":
                    self.__next_char()
                    self.__process_float(token)
            elif self.__char == '"':
                self._process_string(token)
            else:
                if self.__char == "(":
                    token.type = TokenType.LPAR
                    self.__next_char()
                elif self.__char == ")":
                    token.type = TokenType.RPAR
                    self.__next_char()
                elif self.__char == "{":
                    token.type = TokenType.LBRACE
                    self.__next_char()
                elif self.__char == "}":
                    token.type = TokenType.RBRACE
                    self.__next_char()
                elif self.__char == "[":
                    token.type = TokenType.LBRACKET
                    self.__next_char()
                elif self.__char == "]":
                    token.type = TokenType.RBRACKET
                    self.__next_char()
                elif self.__char == ":":
                    self.__next_char()
                    if self.__char == ":":
                        token.type = TokenType.COLON
                        self.__next_char()
                elif self.__char == ";":
                    token.type = TokenType.SEMICOLON
                    self.__next_char()
                elif self.__char == "=":
                    token.type = TokenType.ASSIGN
                    self.__next_char()
                    if self.__char == "=":
                        token.type = TokenType.EQ
                        self.__next_char()
                    elif self.__char == ">":  # Check for 'to' token
                        token.type = TokenType.TO
                        self.__next_char()

                # Arithmetic operators
                elif self.__char == "+":
                    token.type = TokenType.PLUS
                    self.__next_char()
                    if self.__char == "+":
                        token.type = TokenType.UN_ADD
                        self.__next_char()
                elif self.__char == "-":
                    token.type = TokenType.MINUS
                    self.__next_char()
                    if self.__char == "-":  # Check for decrement operator
                        token.type = TokenType.UN_SUB
                        self.__next_char()

                # Multiplicative operators
                elif self.__char == "*":
                    token.type = TokenType.MULTIPLY
                    self.__next_char()
                elif self.__char == "/":
                    token.type = TokenType.DIVIDE
                    self.__next_char()
                elif self.__char == "%":
                    token.type = TokenType.MODULO
                    self.__next_char()

                # Relational operators
                elif self.__char == "!":
                    token.type = TokenType.NOT
                    self.__next_char()
                    if self.__char == "=":
                        token.type = TokenType.NEQ
                        self.__next_char()
                elif self.__char == "|":
                    self.__next_char()
                    if self.__char == "|":
                        token.type = TokenType.OR
                        self.__next_char()
                elif self.__char == "&":
                    self.__next_char()
                    if self.__char == "&":
                        token.type = TokenType.AND
                        self.__next_char()
                elif self.__char == "<":
                    token.type = TokenType.LT
                    self.__next_char()
                    if self.__char == "=":
                        token.type = TokenType.LTE
                        self.__next_char()
                elif self.__char == ">":
                    token.type = TokenType.GT
                    self.__next_char()
                    if self.__char == "=":
                        token.type = TokenType.GTE
                        self.__next_char()

                # Special tokens
                elif self.__char == ",":
                    token.type = TokenType.COMMA
                    self.__next_char()
                elif self.__char == "#":
                    self.__next_char()
                    if self.__char == "#":
                        self.__next_char()
                        self.__skip_comment_block(count=2)
                    else:
                        self.__skip_comment()
                    token = self.get_token()
                else:
                    raise LexerError(
                        f"Unrecognized character '{self.__char}'",
                        self.line_number,
                        self.col_number,
                    )
        else:
            token.type = TokenType.ENDMARKER

        # Remember position for error reporting
        token.position = self.__token_position

        self.__log(f"Token: {token}")
        return token

    def __process_word(self, token: Token) -> None:
        """Scan through the source code and process a found word into a token"""
        processed_word = ""

        while self.__char.isalpha() or self.__char == "_":
            if len(processed_word) + 1 == MAX_ID_LEN:
                raise LexerError(
                    f"Identifier exceeds the maximum length of {MAX_ID_LEN} characters",
                    self.line_number,
                    self.col_number,
                )
            processed_word += self.__char
            self.__next_char()

        if processed_word in RESERVED_WORDS:
            token.word = processed_word
            token.type = RESERVED_WORDS[processed_word]
            return

        token.word = processed_word
        token.type = TokenType.ID

    def __process_number(self, token: Token) -> None:
        """Scan through the source code and process a found number into a token"""
        processed_number = int(self.__char)

        self.__next_char()
        while self.__char.isdigit():
            next_digit = int(self.__char)
            processed_number = (processed_number * 10) + next_digit
            self.__next_char()

        token.number = processed_number
        token.type = TokenType.INT

    def __process_float(self, token: Token) -> None:
        """Scan through the source code and process a found float number into a token"""
        if not isinstance(token.number, int):
            raise LexerError("Invalid float number", self.line_number, self.col_number)

        processed_number = float(self.__char)
        divisor = 10

        self.__next_char()
        while self.__char.isdigit():
            next_digit = int(self.__char)
            processed_number = (processed_number * 10) + next_digit
            divisor *= 10
            self.__next_char()

        processed_fraction = processed_number / divisor
        token.number += processed_fraction
        token.type = TokenType.FLOAT

    def _process_string(self, token: Token) -> None:
        """Scan through the source code and process a found string into a token"""
        processed_string = ""

        self.__next_char()
        while self.__char != '"':
            if self.__char == EOF:
                raise LexerError(
                    "Unterminated string", self.line_number, self.col_number
                )

            if not self.__char.isprintable():
                raise LexerError(
                    f"Non-printable ascii character with code: {ord(self.__char)}",
                    self.line_number,
                    self.col_number,
                )

            if len(processed_string) + 1 > MAX_STR_LEN:
                raise LexerError("String too long", self.line_number, self.col_number)

            if self.__char == "\\":  # Escape characters
                self.__next_char()
                if self.__char == "n":
                    processed_string += "\n"
                elif self.__char == "t":
                    processed_string += "\t"
                elif self.__char == '"':
                    processed_string += '"'
                elif self.__char == "\\":
                    processed_string += "\\"
                else:
                    raise LexerError(
                        "Invalid escape character", self.line_number, self.col_number
                    )
            else:
                processed_string += self.__char
            self.__next_char()

        self.__next_char()
        token.word = processed_string
        token.type = TokenType.STR

    def __skip_comment(self) -> None:
        """Skip a single line comment"""
        while self.__char != "\n":
            self.__next_char()

    def __skip_comment_block(self, count: int) -> None:
        """Skip a block comment"""
        while True:
            if count == 0:
                break

            if self.__char == "#":
                count -= 1
            self.__next_char()

    @property
    def line_number(self) -> int:
        """Returns the line number of the current token"""
        return self.__token_position.line_number

    @property
    def col_number(self) -> int:
        """Returns the column number of the current token"""
        return self.__token_position.column_number

    def __log(self, message: str) -> None:
        """Logs a message if verbose is enabled"""
        if self.__verbose:
            print(message)
