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
    'nai': TokenType.NOT
}


class Lexer(AComponent):
    class __Position:
        def __init__(self, line_number, column_number):
            self.line_number = line_number
            self.column_number = column_number

    def __init__(self):
        super().__init__()
        self.__program = []
        self.__program_counter = 0

        self.__ch = None
        self.__last_read_ch = ""
        self.__line_number = 1
        self.__column_number = 0
        self.__position = self.__Position(1, 0)
        self.__buffer = []

    def __next_char(self):
        """
        Get the next character from the program file
        """
        # Check if last read char was a newline character
        if self.__last_read_ch == '\n':
            # Reset the column number and increment the line number
            self.__line_number += 1
            self.__column_number = 0

        # Check if there are still characters to be processed in the program file
        if self.__program_counter != len(self.__program):
            self.__ch = self.__program[self.__program_counter]

            self.__last_read_ch = self.__ch
            self.__column_number += 1
            self.__program_counter += 1
        else:
            # End of file reached
            self.__ch = EOF

    def analyze_src_file(self, file_path):
        """
        Reads in the source file for tokenization
        @param file_path: the path to the source file
        """
        with open(file_path, "r") as f:
            c = f.read(1)
            while c:
                self.__program.append(c)
                c = f.read(1)
        self.__next_char()

    def analyze_repl(self, repl_input):
        """
        Reads in the REPL input for tokenization
        @param repl_input: the REPL input to be tokenized
        """
        self.__init__()
        self.__program = list(repl_input)
        self.__next_char()

    def peek_token(self):
        """
        Look at the next token, used when parsing the source
        @return: The next token found from the source
        """
        token = self.get_token()
        self.__buffer.append(token)
        return token

    def get_token(self):
        """
        Scans through the source until a recognized symbol or
         keyword is found and returns it as a token object.
        @return: The token found from scanning the source's symbols
        """
        token = Token()

        # Check if there are any tokens in the buffer
        if len(self.__buffer) > 0:
            return self.__buffer.pop(0)

        # Skip whitespace
        while self.__ch.isspace():
            self.__next_char()

        # Remember position for error reporting
        self.__store_position()

        # Scan for tokens
        if self.__ch != EOF:

            if self.__ch.isalpha() or self.__ch == '_':
                self.__process_word(token)
            elif self.__ch.isdigit():
                self.__process_number(token)

                # Check for float
                if self.__ch == '.':
                    self.__next_char()
                    self.__process_float(token)
            elif self.__ch == '"':
                self.__next_char()
                self._process_string(token)
            else:
                if self.__ch == '(':
                    token.type = TokenType.LPAR
                    self.__next_char()
                elif self.__ch == ')':
                    token.type = TokenType.RPAR
                    self.__next_char()
                elif self.__ch == '{':
                    token.type = TokenType.LBRACE
                    self.__next_char()
                elif self.__ch == '}':
                    token.type = TokenType.RBRACE
                    self.__next_char()
                elif self.__ch == ';':
                    token.type = TokenType.SEMICOLON
                    self.__next_char()
                elif self.__ch == '=':
                    self.__next_char()
                    if self.__ch == '=':
                        token.type = TokenType.EQ
                        self.__next_char()
                    elif self.__ch == '>':
                        token.type = TokenType.TO
                        self.__next_char()
                elif self.__ch == '+':
                    self.__next_char()

                    # Check for unary plus
                    if self.__ch == '+':
                        token.type = TokenType.UN_ADD
                        self.__next_char()
                elif self.__ch == '-':
                    token.type = TokenType.NEG
                    self.__next_char()

                    # Check for unary minus
                    if self.__ch == '-':
                        token.type = TokenType.UN_SUB
                        self.__next_char()
                elif self.__ch == '%':
                    token.type = TokenType.MODULO
                    self.__next_char()
                elif self.__ch == '!':
                    token.type = TokenType.NOT
                    self.__next_char()
                    if self.__ch == '=':
                        token.type = TokenType.NEQ
                        self.__next_char()
                elif self.__ch == "#":
                    self.__skip_comment()
                    token = self.get_token()
                elif self.__ch == '<':
                    token.type = TokenType.LT
                    self.__next_char()
                    if self.__ch == '=':
                        token.type = TokenType.LTE
                        self.__next_char()
                elif self.__ch == '>':
                    token.type = TokenType.GT
                    self.__next_char()
                    if self.__ch == '=':
                        token.type = TokenType.GTE
                        self.__next_char()
                elif self.__ch == ',':
                    token.type = TokenType.COMMA
                    self.__next_char()
                else:
                    raise LexerError(f"Unrecognized character '{self.__ch}'",
                                     self.line_number, self.col_number)
        else:
            token.type = TokenType.ENDMARKER

        # Remember position for error reporting
        token.pos = self.__position.line_number, self.__position.column_number

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

        # Read word
        while True:
            if not (self.__ch.isalnum() or self.__ch == '_'):
                break

            # Check for valid characters
            if not self.__ch.isalnum() and self.__ch != '_':
                raise LexerError(f"Invalid character '{self.__ch}' in identifier",
                                 self.line_number, self.col_number)
            # Validate length of word
            if len(processed_word) + 1 == MAX_ID_LEN:
                raise LexerError(f"Identifier exceeds the maximum length of {MAX_ID_LEN} characters",
                                 self.line_number, self.col_number)
            # Append character to word and ge the next character
            processed_word += self.__ch
            self.__next_char()

        # Check for reserved word
        if processed_word in RESERVED_WORDS:
            token.type = RESERVED_WORDS[processed_word]
            return

        # Set token params
        token.value = processed_word
        token.type = TokenType.ID

    def __process_number(self, token):
        """
        Processes found numbers and
        returns a token with its associated type and value (the processed number).
        @param token: The token to assign a type and value to
        @return: The token after processing the number
        """
        # Initialize processed_number with the numeric value of the current character
        processed_number = int(self.__ch)

        self.__next_char()

        # Continue processing while the current character is not an exit symbol
        while self.__ch.isdigit():
            # Calculate the numeric value of the next digit
            next_digit = int(self.__ch)

            # Append the next digit to processed number
            processed_number = (processed_number * 10) + next_digit
            self.__next_char()

        # Set the token's value and type based on the processed number
        token.value = processed_number
        token.type = TokenType.INT

    def __process_float(self, token):
        """
        Processes found floating point numbers and
        returns a token with its associated type and value (the processed float).
        @param token: The token to assign a type and value to
        @return: The token after processing the float
        """
        # Initialize processed_number with the numeric value of the current character
        processed_fraction = float(self.__ch)
        divisor = 10

        self.__next_char()

        # Continue processing while the current character is not an exit symbol
        while self.__ch.isdigit():
            # Increase the divisor
            divisor *= 10

            # Calculate the numeric value of the next digit
            next_digit = int(self.__ch)

            # Append the next digit to processed number
            processed_fraction = (processed_fraction * 10) + next_digit
            self.__next_char()

        # Set the token's value and type based on the processed number
        token.value = token.value + (processed_fraction / divisor)
        token.type = TokenType.FLOAT

    def _process_string(self, token):
        """
        Processes found string literals and
        returns a token with its associated type and value (the processed string)
        @param token: The token to assign a type and value to
        @return: The token after processing the string
        """
        processed_string = ""

        while self.__ch != '"':
            #  Escape characters
            if self.__ch == "\\":
                self.__next_char()
                if self.__ch == 'n':
                    processed_string += '\n'
                elif self.__ch == 't':
                    processed_string += '\t'
                elif self.__ch == '"':
                    processed_string += '"'
                elif self.__ch == '\\':
                    processed_string += '\\'
                else:
                    raise LexerError("Invalid escape character", self.line_number, self.col_number)
            # Reached end of file
            if self.__ch == EOF:
                raise LexerError("Unterminated string", self.line_number, self.col_number)

            # Check for Non-printables
            if not self.__ch.isprintable():
                raise LexerError(f"Non-printable ascii character with code: {ord(self.__ch)}",
                                 self.line_number, self.col_number)
            # Max string length reached
            if len(processed_string) + 1 > MAX_STR_LEN:
                raise LexerError(f"String too long", self.line_number, self.col_number)

            # Concat char to string and get next character
            processed_string += self.__ch
            self.__next_char()
        self.__next_char()

        # Set token params
        token.value = processed_string
        token.type = TokenType.STR

    def __store_position(self):
        """
        Store the current character's line and column number
        """
        self.__position.line_number = self.__line_number
        self.__position.column_number = self.__column_number

    def __skip_comment(self):
        """
        Skips comments found in the source
        """
        while self.__ch != '\n':
            self.__next_char()

    @property
    def line_number(self):
        return self.__position.line_number

    @property
    def col_number(self):
        return self.__position.column_number
