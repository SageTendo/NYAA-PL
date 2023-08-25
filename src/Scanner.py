from Token import TokenType, Token
from ErrorHandler import throw_err

EOF = 'EOF'
MAX_ID_LEN = 32
MAX_STR_LEN = 1024

RESERVED_WORDS = {
    "nyaa_func": TokenType.TOK_NYAA_FUNC,
    "main_nyaa": TokenType.TOK_MAIN_NYAA,
    "say": TokenType.TOK_SAY,
    "listen": TokenType.TOK_LISTEN,
    "give_back": TokenType.TOK_GIVE_BACK,
    "while": TokenType.TOK_WHILE,
    "if": TokenType.TOK_IF,
    "else": TokenType.TOK_ELSE,
    "elif": TokenType.TOK_ELIF,
    "int": TokenType.TOK_INT,
    "str": TokenType.TOK_STR,
}


class Scanner:
    class _Position:
        def __init__(self, line_number, column_number):
            self.line_number = line_number
            self.column_number = column_number

    def __init__(self):
        self.program_file = []
        self.program_counter = 0
        self.tokens = []

        self.ch = None
        self.last_read_ch = ""
        self.column_number = 0
        self.line_number = 1
        self.position = self._Position(1, 0)

    def _next_char(self):
        if self.last_read_ch == '\n':
            self.line_number += 1
            self.column_number = 0

        if self.program_counter != len(self.program_file):
            self.ch = self.program_file[self.program_counter]
            self.column_number += 1
            self.last_read_ch = self.ch
            self.program_counter += 1
        else:
            self.ch = EOF

    def load_src_file(self, file_path):
        with open(file_path, "r") as f:
            c = f.read(1)
            while c:
                self.program_file.append(c)
                c = f.read(1)
        self._next_char()

    def get_token(self, token):
        # Skip whitespace
        while self.ch.isspace():
            self._next_char()

        # Remember position for error reporting
        self._store_position()

        if self.ch != EOF:
            # Read the next token
            if self.ch.isalpha() or self.ch == '_':
                self._process_word(token)
            elif self.ch.isdigit():
                self._process_number(token)
            else:
                if self.ch == '"':
                    self._next_char()
                    self._process_string(token)
                elif self.ch == '(':
                    token.type = TokenType.TOK_LPAR
                    self._next_char()
                elif self.ch == ')':
                    token.type = TokenType.TOK_RPAR
                    self._next_char()
                elif self.ch == '{':
                    token.type = TokenType.TOK_LBRACE
                    self._next_char()
                elif self.ch == '}':
                    token.type = TokenType.TOK_RBRACE
                    self._next_char()
                elif self.ch == ':':
                    self._next_char()
                    if self.ch == ':':
                        token.type = TokenType.TOK_TYPE_ASSIGN
                        self._next_char()
                elif self.ch == ';':
                    token.type = TokenType.TOK_SEMICOLON
                    self._next_char()
                elif self.ch == '=':
                    token.type = TokenType.TOK_ASSIGN
                    self._next_char()
                    if self.ch == '=':
                        token.type = TokenType.TOK_EQ
                        self._next_char()
                elif self.ch == '+':
                    token.type = TokenType.TOK_PLUS
                    self._next_char()
                elif self.ch == '-':
                    token.type = TokenType.TOK_MINUS
                    self._next_char()
                elif self.ch == '*':
                    token.type = TokenType.TOK_MULTIPLY
                    self._next_char()
                elif self.ch == '/':
                    token.type = TokenType.TOK_DIVIDE
                    self._next_char()
                elif self.ch == '%':
                    token.type = TokenType.TOK_MODULO
                    self._next_char()
                elif self.ch == '&':
                    self._next_char()
                    if self.ch == '&':
                        token.type = TokenType.TOK_AND
                        self._next_char()
                elif self.ch == '|':
                    self._next_char()
                    if self.ch == '|':
                        token.type = TokenType.TOK_OR
                        self._next_char()
                elif self.ch == '!':
                    token.type = TokenType.TOK_NOT
                    self._next_char()
                    if self.ch == '=':
                        token.type = TokenType.TOK_NEQ
                        self._next_char()
                elif self.ch == "#":
                    self._skip_comment()
                    self.get_token(token)
                elif self.ch == '<':
                    token.type = TokenType.TOK_LT
                    self._next_char()
                    if self.ch == '=':
                        token.type = TokenType.TOK_LTE
                        self._next_char()
                elif self.ch == '>':
                    token.type = TokenType.TOK_GT
                    self._next_char()
                    if self.ch == '=':
                        token.type = TokenType.TOK_GTE
                        self._next_char()

        else:
            token.type = TokenType.TOK_EOF
        print(token)

    def _process_word(self, token):
        processed_word = ""
        # Read word
        while True:
            if self.ch in [' ', '\t', '\n', '(', ')', '{', '}', ':', ';', '=']:
                break

            if not self.ch.isalnum() and self.ch != '_':
                throw_err(f"Unexpected character: '{self.ch}' at {self.position.line_number}:{self.column_number}")

            if len(processed_word) + 1 == MAX_ID_LEN:
                throw_err(f"Identifier too long: {processed_word}")

            processed_word += self.ch
            self._next_char()

        # Check for reserved words
        if processed_word in RESERVED_WORDS:
            token.type = RESERVED_WORDS[processed_word]
            return

        token.word = processed_word
        token.type = TokenType.TOK_ID

    def _process_number(self, token):
        processed_number = ord(self.ch) - ord('0')
        self._next_char()

        while True:
            if self.ch in [' ', '\t', '\n', '(', ')', '{', '}', ':', ';', '=']:
                break

            next_digit = ord(self.ch) - ord('0')
            if next_digit < 0 or next_digit > 9:
                throw_err(f"Unexpected character: '{self.ch}' at {self.position.line_number}:{self.column_number}")

            processed_number = (processed_number * 10) + next_digit
            self._next_char()

        token.value = processed_number
        token.type = TokenType.TOK_INT

    def _process_string(self, token):
        processed_string = ""
        while self.ch != '"':
            if self.ch == "\\":
                self._next_char()
                if self.ch == 'n':
                    processed_string += '\n'
                elif self.ch == 't':
                    processed_string += '\t'
                elif self.ch == '"':
                    processed_string += '"'
                elif self.ch == '\\':
                    processed_string += '\\'
                else:
                    throw_err(
                        f"Unexpected escape character: '{self.ch}' at {self.position.line_number}:{self.column_number}")

            if self.ch == EOF:
                throw_err(f"Unterminated string at {self.position.line_number}:{self.position.column_number}")

            if not self.ch.isprintable():
                throw_err(
                    f"Non-printable ascii character with code: "
                    f"{ord(self.ch)} at {self.position.line_number}:{self.column_number}")

            if len(processed_string) + 1 > MAX_STR_LEN:
                throw_err(f"String too long at {self.position.line_number}:{self.position.column_number}")

            processed_string += self.ch
            self._next_char()
        self._next_char()

        token.value = processed_string
        token.type = TokenType.TOK_STR

    def _store_position(self):
        self.position.line_number = self.line_number
        self.position.column_number = self.column_number

    def _skip_comment(self):
        while self.ch != '\n':
            self._next_char()


if __name__ == '__main__':
    # Testing purpose
    scanner = Scanner()

    import sys

    sys.tracebacklimit = 0
    filepath = sys.argv[1]
    scanner.load_src_file(filepath)

    tokens = []
    while True:
        tkn = Token()
        scanner.get_token(tkn)

        if tkn.type == TokenType.TOK_EOF:
            break
