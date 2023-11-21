from src.Token import Token
from src.Types import TokenType
from src.utils.Constants import EOF, MAX_ID_LEN, MAX_STR_LEN
from src.utils.ErrorHandler import throw_err, throw_unexpected_char_err

RESERVED_WORDS = {
    "uWu_nyaa": TokenType.MAIN,
    "purinto": TokenType.PRINT,
    "ohayo": TokenType.INPUT,
    "daijoubu": TokenType.WHILE,
    "nani": TokenType.IF,
    "nandesuka": TokenType.ELIF,
    "baka": TokenType.ELSE,
    'yamete': TokenType.BREAK,
    'pasu': TokenType.PASS,
    'motto': TokenType.CONTINUE,
    'kawaii': TokenType.DEF,
    'ganbatte': TokenType.TRY,
    'gomenasai': TokenType.EXCEPT,
    'HAI': TokenType.TRUE,
    'IIE': TokenType.FALSE,
    'asain': TokenType.ASSIGN,
    "sayonara": TokenType.RET,
    'purasu': TokenType.PLUS,
    'mainasu': TokenType.MINUS,
    'purodakuto': TokenType.MULTIPLY,
    'supuritto': TokenType.DIVIDE,
    'ando': TokenType.AND,
    'matawa': TokenType.OR,
    'nai': TokenType.NOT
}

EXIT_SYMBOLS = [' ', '\t', '\n',
                '(', ')', ':',
                ';', '=', '[',
                ']', '+', '-',
                '*', '/', '%',
                '!', '<', '>',
                '&', '|', ',',
                EOF
                ]


class Lexer:
    class _Position:
        def __init__(self, line_number, column_number):
            self.line_number = line_number
            self.column_number = column_number

    __debug_mode = False

    def __init__(self):
        self.__program_file = []
        self.__program_counter = 0

        self.__ch = None
        self.__last_read_ch = ""
        self.__column_number = 0
        self.__line_number = 1
        self.__position = self._Position(1, 0)
        self.__buffer = []

    def _next_char(self):
        """
        Get the next character from the program file
        """
        # Check if last read char was a newline character
        if self.__last_read_ch == '\n':
            # Reset the column number and increment the line number
            self.__line_number += 1
            self.__column_number = 0

        # Check if there are still characters to be processed in the program file
        if self.__program_counter != len(self.__program_file):
            self.__ch = self.__program_file[self.__program_counter]

            self.__last_read_ch = self.__ch
            self.__column_number += 1
            self.__program_counter += 1
        else:
            # End of file reached
            self.__ch = EOF

    def load_src_file(self, file_path):
        """
        Reads in the source file for tokenization
        @param file_path: the path to the source file
        """
        with open(file_path, "r") as f:
            c = f.read(1)
            while c:
                self.__program_file.append(c)
                c = f.read(1)
        self._next_char()

    def peek_token(self):
        token = self.get_token()
        self.__buffer.append(token)
        return token

    def get_token(self):
        token = Token()

        # Check if there are any tokens in the buffer
        if len(self.__buffer) > 0:
            return self.__buffer.pop(0)

        # Skip whitespace
        while self.__ch.isspace():
            self._next_char()

        # Remember position for error reporting
        self._store_position()

        # Scan for tokens
        if self.__ch != EOF:

            if self.__ch.isalpha() or self.__ch == '_':
                self._process_word(token)
            elif self.__ch.isdigit():
                self._process_number(token)
            elif self.__ch == '"':
                self._next_char()
                self._process_string(token)
            else:
                if self.__ch == '(':
                    token.type = TokenType.LPAR
                    self._next_char()
                elif self.__ch == ')':
                    token.type = TokenType.RPAR
                    self._next_char()
                elif self.__ch == '{':
                    token.type = TokenType.LBRACE
                    self._next_char()
                elif self.__ch == '}':
                    token.type = TokenType.RBRACE
                    self._next_char()
                elif self.__ch == ';':
                    token.type = TokenType.SEMICOLON
                    self._next_char()
                elif self.__ch == '=':
                    self._next_char()
                    if self.__ch == '=':
                        token.type = TokenType.EQ
                        self._next_char()
                    elif self.__ch == '>':
                        token.type = TokenType.TO
                        self._next_char()
                elif self.__ch == '+':
                    self._next_char()
                    if self.__ch == '+':
                        token.type = TokenType.UN_ADD
                        self._next_char()
                elif self.__ch == '-':
                    token.type = TokenType.NEG
                    self._next_char()
                    if self.__ch == '-':
                        token.type = TokenType.UN_SUB
                        self._next_char()
                elif self.__ch == '%':
                    token.type = TokenType.MODULO
                    self._next_char()
                elif self.__ch == '!':
                    token.type = TokenType.NOT
                    self._next_char()
                    if self.__ch == '=':
                        token.type = TokenType.NEQ
                        self._next_char()
                elif self.__ch == "#":
                    self._skip_comment()
                    token = self.get_token()
                elif self.__ch == '<':
                    token.type = TokenType.LT
                    self._next_char()
                    if self.__ch == '=':
                        token.type = TokenType.LTE
                        self._next_char()
                elif self.__ch == '>':
                    token.type = TokenType.GT
                    self._next_char()
                    if self.__ch == '=':
                        token.type = TokenType.GTE
                        self._next_char()
                elif self.__ch == ',':
                    token.type = TokenType.COMMA
                    self._next_char()
                elif self.__ch == '.':
                    token.type = TokenType.PERIOD
                    self._next_char()
        else:
            token.type = TokenType.ENDMARKER

        self.validate(token)
        return token

    def _process_word(self, token):
        processed_word = ""

        # Read word
        while True:
            if self.__ch in EXIT_SYMBOLS:
                break

            # Check for valid characters
            if not self.__ch.isalnum() and self.__ch != '_':
                throw_err(
                    f"Unexpected character: '{self.__ch}' at "
                    f"{self.__position.line_number}:{self.__column_number}")

            # Validate length of word
            if len(processed_word) + 1 == MAX_ID_LEN:
                throw_err(f"Identifier too long: {processed_word}")

            # Append character to word and ge the next character
            processed_word += self.__ch
            self._next_char()

        # Check for reserved word
        if processed_word in RESERVED_WORDS:
            token.type = RESERVED_WORDS[processed_word]
            return

        # Set token params
        token.value = processed_word
        token.type = TokenType.ID

    def _process_number(self, token):
        # Initialize processed_number with the numeric value of the current character
        processed_number = ord(self.__ch) - ord('0')

        self._next_char()

        # Continue processing while the current character is not an exit symbol
        while True:
            if self.__ch in EXIT_SYMBOLS:
                break

            # Calculate the numeric value of the next digit
            next_digit = ord(self.__ch) - ord('0')

            #  Check if valid digit
            if next_digit < 0 or next_digit > 9:
                throw_err(
                    f"Unexpected character: '{self.__ch}' at "
                    f"{self.__position.line_number}:{self.__column_number}")

            # Append the next digit to processed number
            processed_number = (processed_number * 10) + next_digit
            self._next_char()

        # Set the token's value and type based on the processed number
        token.value = processed_number
        token.type = TokenType.INT

    def _process_string(self, token):
        processed_string = ""

        while self.__ch != '"':
            #  Escape characters
            if self.__ch == "\\":
                self._next_char()
                if self.__ch == 'n':
                    processed_string += '\n'
                elif self.__ch == 't':
                    processed_string += '\t'
                elif self.__ch == '"':
                    processed_string += '"'
                elif self.__ch == '\\':
                    processed_string += '\\'
                else:
                    throw_err(f"Unexpected escape character: "
                              f"'{self.__ch}' at {self.__position.line_number}:{self.__column_number}")

            # Reached end of file
            if self.__ch == EOF:
                throw_err(f"Unterminated string at {self.__position.line_number}:{self.__position.column_number}")

            # Check for Non-printables
            if not self.__ch.isprintable():
                throw_err(
                    f"Non-printable ascii character with code: "
                    f"{ord(self.__ch)} at {self.__position.line_number}:{self.__column_number}")

            # Max string length reached
            if len(processed_string) + 1 > MAX_STR_LEN:
                throw_err(f"String too long at "
                          f"{self.__position.line_number}:{self.__position.column_number}")

            # Concat char to string and get next character
            processed_string += self.__ch
            self._next_char()
        self._next_char()

        # Set token params
        token.value = processed_string
        token.type = TokenType.STR

    def _store_position(self):
        """
        Store the current character's line and column number
        """
        self.__position.line_number = self.__line_number
        self.__position.column_number = self.__column_number

    def _skip_comment(self):
        while self.__ch != '\n':
            self._next_char()

    def get_last_read(self):
        return self.__last_read_ch

    def get_line_number(self):
        return self.__position.line_number

    def get_col_number(self):
        return self.__position.column_number

    def debug_info(self, token):
        if self.__debug_mode:
            print(token)

    def verbose(self, debug_mode=False):
        self.__debug_mode = debug_mode

    def validate(self, token):
        if self.__debug_mode:
            print(token)

        if not token.type:
            throw_unexpected_char_err(self.__ch, self.__position.line_number, self.__position.column_number)
        return token
