from src.core.ASTNodes import BodyNode
from src.core.RuntimeObject import RunTimeObject


class Symbol:
    """Represents a symbol held by the symbol table"""

    def __init__(self, name: str):
        """
        Initializes a new symbol
        @param name: The name of the symbol
        @param value: The value of the symbol
        """
        self.__symbol_name = name

    @property
    def name(self):
        """Return the name of the symbol"""
        return self.__symbol_name

    def __hash__(self):
        """Return the hash of the symbol"""
        return hash(self.__symbol_name)

    def __eq__(self, other: "Symbol") -> bool:
        """
        Checks if the symbol is equal to another symbol
        @param other: The other symbol to compare with
        @return: True if the symbols are equal, false otherwise
        """
        if not (isinstance(self, super) and isinstance(other, super)):
            return False
        return self == other


class VarSymbol(Symbol):
    """Represents a variable"""

    def __init__(self, name: str, value: RunTimeObject):
        """
        Initializes a new variable symbol
        @param name: The name of the variable
        @param value: The value held by the variable (instance of RunTimeObject)
        """
        super().__init__(name)
        self.__value = value

    @property
    def value(self) -> RunTimeObject:
        """Return the value of the variable"""
        return self.__value


class FunctionSymbol(Symbol):
    """Represents a function"""

    def __init__(self, name: str, params: dict, body: BodyNode):
        """
        Initializes a new function symbol
        @param name: The name of the function
        @param params: The parameters of the function
        @param body: The body of the function
        """
        super().__init__(name)
        self.__params = params
        self.__body = body

    @property
    def params(self) -> dict:
        """Return the parameters of the function"""
        return self.__params

    @property
    def body(self) -> BodyNode:
        """Return the body of the function"""
        return self.__body


class ArraySymbol(Symbol):
    """Represents an array"""

    def __init__(self, name: str, size: int, values: list[RunTimeObject]):
        """
        Initializes a new array symbol
        @param name: The name of the array
        @param size: The size of the array
        @param values: The values held by the array
        """
        super().__init__(name)
        self.values = values
        self.size = size
