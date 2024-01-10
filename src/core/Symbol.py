class Symbol:
    def __init__(self, name, value):
        self.__symbol_name = name
        self.__symbol_value = value

    @property
    def name(self):
        """
        @return: The name of the symbol
        """
        return self.__symbol_name

    @property
    def value(self):
        """
        @return: The value of the symbol
        """
        return self.__symbol_value

    def __hash__(self):
        """
        @return: The hash of the symbol
        """
        return hash(self.__symbol_name)

    def __eq__(self, other):
        """
        Checks if the symbol is equal to another symbol
        @param other: The other symbol to compare with
        @return: True if the symbols are equal, false otherwise
        """
        if not (isinstance(self, super) and isinstance(other, super)):
            return False
        return self == other


class VarSymbol(Symbol):
    def __init__(self, name, value):
        super().__init__(name, value)


class FunctionSymbol(Symbol):
    def __init__(self, name, params, body):
        super().__init__(name, None)
        self.__params = params
        self.__body = body

    @property
    def params(self):
        return self.__params

    @property
    def body(self):
        return self.__body


class ArraySymbol(Symbol):
    def __init__(self, name, size=None, values=None):
        super().__init__(name, None)
        self.values = values
        self.size = size
