from src.core.Symbol import VarSymbol, FunctionSymbol


class Environment:
    def __init__(self, name, level, parent=None):
        self.__name = name
        self.__level = level
        self.__parent = parent
        self.__symbol_table = {}

    def insert_variable(self, name: str, value: 'RunTimeObject'):
        """
        Adds a variable to the symbol table along with its value.
        @param name: The name of the variable.
        @param value: The value of the variable.
        """
        self.__symbol_table[name] = VarSymbol(name, value)

    def lookup_variable(self, name, current_scope=False) -> 'RunTimeObject':
        """
        Retrieves the value of a given variable.
        If the current scope flag is not set,
        lookups will be performed on the current scope and all parent scopes
        @param name: The name of the variable.
        @param current_scope: Flag to restrict lookups to the current scope
        @return: The value of the variable.
        @raise Exception: If the variable is not found in the table.
        """
        var_symbol = self.__symbol_table.get(name, None)
        if var_symbol and isinstance(var_symbol, VarSymbol):
            return var_symbol.value

        if not current_scope and self.parent:
            return self.parent.lookup_variable(name)

        raise Exception(f"Variable '{name}' not found in '{self.__name}' scope")

    def insert_function(self, name: str, params: dict, body: 'BodyNode'):
        """
        Adds a function to the symbol table along with its properties.
        @param body: The body node of the function.
        @param params: The parameters of the function in the form of a dictionary.
        @param name: The name of the function.
        @raise Exception: If the function already exists in the table.
        """
        self.__symbol_table[name] = FunctionSymbol(name, params, body)

    def lookup_function(self, name, current_scope=False) -> 'FunctionSymbol':
        """
        Retrieves the symbol of a given function.
        If the current scope flag is not set, lookups will be performed
        on the current scope and all parent scopes.
        @param name: The name of the function.
        @param current_scope: Flag to restrict lookups to the current scope
        @return: The symbol of the function.
        """
        function_symbol = self.__symbol_table.get(name, None)
        if function_symbol and isinstance(function_symbol, FunctionSymbol):
            return function_symbol

        if not current_scope and self.parent:
            return self.parent.lookup_function(name)

        raise Exception(f"Function '{name}' not found in '{self.__name}' scope")

    @property
    def name(self):
        return self.__name

    @property
    def level(self):
        return self.__level

    @property
    def parent(self):
        return self.__parent

    def __str__(self):
        """
        @return: The string representation of the symbol table
        """
        table = []
        for k, v in sorted(self.__symbol_table.items()):
            if isinstance(v, VarSymbol):
                table.append(f"Var: {k} =>\n"
                             f"  Value: {v.value}")
            elif isinstance(v, FunctionSymbol) == 'func':
                table.append(f"Func: {k}] =>\n"
                             f"  Params: {v.params}\n"
                             f"  Body: {v.body}")
        return '\n'.join(table)

    def __hash__(self):
        """
        @return: The hash value of the symbol table
        """
        return hash(self.__str__())
