class Token:
    def __init__(self):
        self._type = None
        self._value = None
        self._word = None
        self._string = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, tok_type):
        self._type = tok_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def word(self):
        return self._word

    @word.setter
    def word(self, word):
        self._word = word

    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, string):
        self._string = string

    def __str__(self):
        val = None
        if self._value is not None:
            val = self._value
        elif self._word is not None:
            val = self._word
        elif self._string is not None:
            val = self._string

        if val is not None:
            return f"type: {self._type} -> {val}"
        return f"type: {self._type}"
