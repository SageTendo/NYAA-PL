import hashlib
from typing import Any, Dict, Optional

from src.core.RuntimeObject import RunTimeObject
from src.core.Symbol import ArraySymbol, FunctionSymbol, Symbol, VarSymbol


class Environment:
    def __init__(self, name: str, level: int, parent: Optional["Environment"] = None):
        self.__name = name
        self.__level = level
        self.__parent = parent
        self.__symbol_table: Dict[str, Symbol] = {}

    def insert_symbol(self, name: str, symbol: Any):
        """
        Inserts a symbol into the symbol table
        @param name: The name of the symbol
        @param symbol: The symbol to insert
        """
        self.__symbol_table[name] = symbol

    def lookup_symbol(self, name: str, lookup_within_scope=False) -> RunTimeObject:
        """
        Retrieves the runtime object of the specified symbol from the symbol table.
        If the lookup_within_scope flag is not set,
        lookups will be performed on the current scope and all parent scopes
        @param name: The name of the symbol.
        @param lookup_within_scope: Flag to restrict lookups to the current scope
        @return: The runtime object representing the symbol.
        @raise Exception: If the symbol is not found in the table.
        """
        symbol = self.__symbol_table.get(name, None)
        if symbol and isinstance(symbol, VarSymbol):
            return symbol.value

        if not lookup_within_scope and self.parent:
            return self.parent.lookup_symbol(name)

        raise Exception(f"Variable '{name}' not found in '{self.__name}' scope")

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
                table.append(f"Var: {k} =>\n  Value: {v.value}")
            elif isinstance(v, FunctionSymbol) == "func":
                table.append(f"Func: {k}] =>\n  Params: {v.params}\n  Body: {v.body}")
            elif isinstance(v, ArraySymbol):
                table.append(f"Array: {k} =>\n  Size: {v.size}\n  Values: {v.values}")
        return "\n".join(table)

    def __hash__(self):
        """Return the hash value of the symbol table"""
        return self.hash()
