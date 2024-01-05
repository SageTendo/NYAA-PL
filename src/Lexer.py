from src.core.AComponent import AComponent
from src.core.Token import Token
from src.core.Types import TokenType
from src.utils.Constants import EOF, MAX_ID_LEN, MAX_STR_LEN
from src.utils.ErrorHandler import LexerError

RESERVED_WORDS = {
    "uWu_nyaa": TokenType.MAIN, "yomu": TokenType.PRINT, "ohayo": TokenType.INPUT,
    "daijoubu": TokenType.WHILE, "nani": TokenType.IF, "nandesuka": TokenType.ELIF,
    "baka": TokenType.ELSE, 'yamete': TokenType.BREAK, 'pasu': TokenType.PASS,
    'motto': TokenType.CONTINUE, 'kawaii': TokenType.DEF, 'HAI': TokenType.TRUE,
    'IIE': TokenType.FALSE, 'wa': TokenType.ASSIGN, "modoru": TokenType.RET,
    'purasu': TokenType.PLUS, 'mainasu': TokenType.MINUS, 'purodakuto': TokenType.MULTIPLY,
    'supuritto': TokenType.DIVIDE, 'ando': TokenType.AND, 'matawa': TokenType.OR,
    'nai': TokenType.NOT, 'for': TokenType.FOR
}


class Lexer(AComponent):
    class __Position:
        def __init__(self, line_number, column_number):
            self.line_number = line_number
            self.column_number = column_number

    def __init__(self):
        super().__init__()
        self.__program_buffer = []
        self.__program_counter = 0

        self.__current_char = None
        self.__last_read_char = ""
        self.__line_number = 1
        self.__column_number = 0
        self.__position = self.__Position(1, 0)
        self.__token_buffer = []

    def __next_char(self):
        """
        Get the next character from the program file
        """
        if self.__last_read_char == '\n':
            self.__line_number += 1
            self.__column_number = 0

        if self.__program_counter != len(self.__program_buffer):
            self.__current_char = self.__program_buffer[self.__program_counter]
            self.__last_read_char = self.__current_char
            self.__column_number += 1
            self.__program_counter += 1
        else:
            self.__current_char = EOF

    def analyze_src_file(self, source_file):
        """
        Reads in the source file for tokenization
        @param source_file: the source file to scan
        """
        with open(source_file, "r") as source:
            c = source.read(1)
            while c:
                self.__program_buffer.append(c)
                c = source.read(1)
        self.__next_char()

    def analyze_repl(self, repl_input):
        """
        Reads in the REPL input for tokenization
        @param repl_input: the REPL input to be tokenized
        """
        self.__init__()
        self.__program_buffer = list(repl_input)
        self.__next_char()

    def peek_token(self):
        """
        Look at the next token, used when parsing the source
        @return: The next token found from the source
        """
        token = self.get_token()
        self.__token_buffer.append(token)
        return token

    def get_token(self):
        """
        Scans through the source until a recognized symbol or
        keyword is found and returns it as a token object.
        @return: The token found from scanning the source's symbols
        """
        if len(self.__token_buffer) > 0:
            return self.__token_buffer.pop(0)

        token = Token()
        while self.char.isspace():
            self.__next_char()

        self.__store_position()  # Remember position for error reporting
        if self.char != EOF:

            if self.char.isalpha() or self.char == '_':
                self.__process_word(token)
            elif self.char.isdigit():
                self.__process_number(token)

                if self.char == '.':
                    self.__next_char()
                    self.__process_float(token)
            elif self.char == '"':
                self._process_string(token)
            else:

                if self.char == '(':
                    token.type = TokenType.LPAR
                    self.__next_char()
                elif self.char == ')':
                    token.type = TokenType.RPAR
                    self.__next_char()
                elif self.char == '{':
                    token.type = TokenType.LBRACE
                    self.__next_char()
                elif self.char == '}':
                    token.type = TokenType.RBRACE
                    self.__next_char()
                elif self.char == ':':
                    self.__next_char()

                    if self.char == ':':
                        token.type = TokenType.DCOLON
                        self.__next_char()
                elif self.char == ';':
                    token.type = TokenType.SEMICOLON
                    self.__next_char()
                elif self.char == '=':
                    self.__next_char()

                    if self.char == '=':
                        token.type = TokenType.EQ
                        self.__next_char()
                    elif self.char == '>':  # Check for 'to' token
                        token.type = TokenType.TO
                        self.__next_char()

                elif self.char == '+':
                    self.__next_char()

                    if self.char == '+':
                        token.type = TokenType.UN_ADD
                        self.__next_char()

                elif self.char == '-':
                    token.type = TokenType.NEG

                    # Check for unary minus
                    self.__next_char()
                    if self.char == '-':
                        token.type = TokenType.UN_SUB
                        self.__next_char()

                elif self.char == '%':
                    token.type = TokenType.MODULO
                    self.__next_char()
                elif self.char == '!':
                    token.type = TokenType.NOT

                    self.__next_char()
                    if self.char == '=':
                        token.type = TokenType.NEQ
                        self.__next_char()

                elif self.char == "#":
                    self.__skip_comment()
                    token = self.get_token()
                elif self.char == '<':
                    token.type = TokenType.LT

                    self.__next_char()
                    if self.char == '=':
                        token.type = TokenType.LTE
                        self.__next_char()

                elif self.char == '>':
                    token.type = TokenType.GT

                    self.__next_char()
                    if self.char == '=':
                        token.type = TokenType.GTE
                        self.__next_char()

                elif self.char == ',':
                    token.type = TokenType.COMMA
                    self.__next_char()
                else:
                    raise LexerError(f"Unrecognized character '{self.char}'",
                                     self.line_number, self.col_number)
        else:
            token.type = TokenType.ENDMARKER

        token.pos = self.__position.line_number, self.__position.column_number  # Remember position for error reporting
        self.debug(token)
        return token

    def __process_word(self, token):
        """
        Processes found identifiers or reserved words and
        returns a token with its associated type and value (the processed word).
        @param token: The token to assign a type and value to
        @return: The token after processing the word
        """
        processed_word = ""

        while self.char.isalpha() or self.char == '_':
            if len(processed_word) + 1 == MAX_ID_LEN:
                raise LexerError(f"Identifier exceeds the maximum length of {MAX_ID_LEN} characters",
                                 self.line_number, self.col_number)
            processed_word += self.char
            self.__next_char()

        if processed_word in RESERVED_WORDS:
            token.value = processed_word
            token.type = RESERVED_WORDS[processed_word]
            return

        token.value = processed_word
        token.type = TokenType.ID

    def __process_number(self, token):
        """
        Processes found numbers and  returns a token with its associated type and value (the processed number).
        @param token: The token to assign a type and value to
        @return: The token after processing the number
        """
        processed_number = int(self.char)

        self.__next_char()
        while self.char.isdigit():
            next_digit = int(self.char)
            processed_number = (processed_number * 10) + next_digit  # Append the next digit to processed number
            self.__next_char()

        token.value = processed_number
        token.type = TokenType.INT

    def __process_float(self, token):
        """
        Processes found floating point numbers and returns a token with its associated type and value.
        @param token: The token to assign a type and value to
        @return: The token after processing the float
        """
        processed_number = float(self.char)
        divisor = 10

        self.__next_char()
        while self.char.isdigit():
            next_digit = int(self.char)
            processed_number = (processed_number * 10) + next_digit
            divisor *= 10

            self.__next_char()

        processed_fraction = processed_number / divisor
        token.value = token.value + processed_fraction
        token.type = TokenType.FLOAT

    def _process_string(self, token):
        """
        Processes found string literals and
        returns a token with its associated type and value (the processed string)
        @param token: The token to assign a type and value to
        @return: The token after processing the string
        """
        processed_string = ""

        self.__next_char()
        while self.char != '"':

            if self.char == EOF:
                raise LexerError("Unterminated string", self.line_number, self.col_number)

            if not self.char.isprintable():
                raise LexerError(f"Non-printable ascii character with code: {ord(self.char)}",
                                 self.line_number, self.col_number)

            if len(processed_string) + 1 > MAX_STR_LEN:
                raise LexerError(f"String too long", self.line_number, self.col_number)

            if self.char == "\\":  # Escape characters
                self.__next_char()
                if self.char == 'n':
                    processed_string += '\n'
                elif self.char == 't':
                    processed_string += '\t'
                elif self.char == '"':
                    processed_string += '"'
                elif self.char == '\\':
                    processed_string += '\\'
                else:
                    raise LexerError("Invalid escape character", self.line_number, self.col_number)

            processed_string += self.char
            self.__next_char()

        self.__next_char()
        token.value = processed_string
        token.type = TokenType.STR

    def __store_position(self):
        self.__position.line_number = self.__line_number
        self.__position.column_number = self.__column_number

    def __skip_comment(self):
        while self.char != '\n':
            self.__next_char()

    @property
    def line_number(self):
        return self.__position.line_number

    @property
    def col_number(self):
        return self.__position.column_number

    @property
    def char(self):
        return self.__current_char
