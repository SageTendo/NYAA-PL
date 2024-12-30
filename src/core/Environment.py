import hashlib
from typing import Any, Dict, Optional

from src.core.ASTNodes import BodyNode
from src.core.RuntimeObject import RunTimeObject
from src.core.Symbol import VarSymbol, FunctionSymbol, ArraySymbol


class Environment:
    def __init__(self, name: str, level: int, parent: Optional["Environment"] = None):
        self.__name = name
        self.__level = level
        self.__parent = parent
        self.__symbol_table: Dict[str, Any] = {}

    def insert_variable(self, name: str, value: RunTimeObject):
        """
        Adds a variable to the symbol table along with its value.
        @param name: The name of the variable.
        @param value: The value of the variable.
        """
        self.__symbol_table[name] = VarSymbol(name, value)

    def lookup_variable(self, name: str, lookup_within_scope=False) -> RunTimeObject:
        """
        Retrieves the value of a given variable.
        If the lookup_within_scope flag is not set,
        lookups will be performed on the current scope and all parent scopes
        @param name: The name of the variable.
        @param lookup_within_scope: Flag to restrict lookups to the current scope
        @return: The value of the variable.
        @raise Exception: If the variable is not found in the table.
        """
        var_symbol = self.__symbol_table.get(name, None)
        if var_symbol and isinstance(var_symbol, VarSymbol):
            return var_symbol.value

        if not lookup_within_scope and self.parent:
            return self.parent.lookup_variable(name)

        raise Exception(f"Variable '{name}' not found in '{self.__name}' scope")

    def insert_function(self, name: str, params: dict, body: BodyNode):
        """
        Adds a function to the symbol table along with its properties.
        @param body: The body node of the function.
        @param params: The parameters of the function in the form of a dictionary.
        @param name: The name of the function.
        @raise Exception: If the function already exists in the table.
        """
        self.__symbol_table[name] = FunctionSymbol(name, params, body)

    def lookup_function(self, name: str, lookup_within_scope=False) -> FunctionSymbol:
        """
        Retrieves the symbol of a given function.
        If the 'lookup_within_scope' flag is not set, lookups will be performed
        on the current scope and all parent scopes.
        @param name: The name of the function.
        @param lookup_within_scope: Flag to restrict lookups to the current scope
        @return: The symbol of the function.
        """
        function_symbol = self.__symbol_table.get(name, None)
        if function_symbol and isinstance(function_symbol, FunctionSymbol):
            return function_symbol

        if not lookup_within_scope and self.parent:
            return self.parent.lookup_function(name)

        raise Exception(f"Function '{name}' not found in '{self.__name}' scope")

    def insert_array(self, name: str, array: "ArraySymbol"):
        """
        Inserts an array into the symbol table.
        @param name: The name of the array.
        @param array: The array symbol.
        """
        self.__symbol_table[name] = array

    def lookup_array(self, name: str, lookup_within_scope=False) -> ArraySymbol:
        """
        Looks up an array in the symbol table.
        If the 'lookup_within_scope' flag is not set, lookups will be performed
        on the current scope and all parent scopes.
        @param name: The name of the array.
        @param lookup_within_scope: Flag to restrict lookups to the current scope
        @return: The array symbol.
        """
        array = self.__symbol_table.get(name, None)
        if array and isinstance(array, ArraySymbol):
            return array

        if not lookup_within_scope and self.parent:
            return self.parent.lookup_array(name)

        raise Exception(f"Array '{name}' not found in '{self.__name}' scope")

    @property
    def name(self):
        """Get the name of the environment"""
        return self.__name

    @property
    def level(self):
        """Get the scope level of the environment"""
        return self.__level

    @property
    def parent(self):
        """Get the parent environment of the current environment"""
        return self.__parent

    def hash(self):
        """Hash the symbol table"""
        return hashlib.sha256(self.__str__().encode()).hexdigest()

    def __str__(self):
        """
        Return a string representation of the symbol table.
        The symbol table is sorted by key to ensure consistent output for hash generation.
        """
        table = []
        for k, v in sorted(self.__symbol_table.items()):
            if isinstance(v, VarSymbol):
                table.append(f"Var: {k} =>\n" f"  Value: {v.value}")
            elif isinstance(v, FunctionSymbol) == "func":
                table.append(
                    f"Func: {k}] =>\n" f"  Params: {v.params}\n" f"  Body: {v.body}"
                )
            elif isinstance(v, ArraySymbol):
                table.append(
                    f"Array: {k} =>\n" f"  Size: {v.size}\n" f"  Values: {v.values}"
                )
        return "\n".join(table)

    def __hash__(self):
        """Return the hash value of the symbol table"""
        return self.hash()
