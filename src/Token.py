class Token:
    def __init__(self):
        self._type = None
        self._value = None

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

    def __str__(self):
        val = None
        if self._value is not None:
            val = self._value

        if val is not None:
            return f"type: {self._type} -> {val}"
        return f"type: {self._type}"
