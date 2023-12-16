class SymbolTable:
    def __init__(self):
        self.__table = {}

    def add_variable(self, name: str, value: 'RunTimeObject'):
        """
        Adds a variable to the symbol table along with its value.
        @param name: The name of the variable.
        @param value: The value of the variable.
        """
        key = (name, 'id')
        self.__table[key] = value

    def get_variable(self, name):
        """
        Retrieves the value of a given variable.
        @param name: The name of the variable.
        @return: The value of the variable.
        @raise Exception: If the variable is not found in the table.
        """
        key = (name, 'id')
        if key not in self.__table:
            raise Exception(f"Variable '{name}' not found")
        return self.__table[key]

    def add_function_props(self, name: str, value: dict):
        """
        Adds a function to the symbol table along with its properties.
        @param name: The name of the function.
        @param value: The properties of the function.
        @raise Exception: If the function already exists in the table.
        """
        key = (name, 'func')

        if key in self.__table:
            raise Exception(f"Function '{name}' already exists")
        self.__table[key] = value

    def get_function_props(self, name):
        """
        Retrieves the properties of a given function.
        @param name: The name of the function.
        @return: The properties of the function.
        @raise Exception: If the function is not found in the table.
        """
        key = (name, 'func')

        if key not in self.__table:
            raise Exception(f"Function '{name}' not found")
        return self.__table[key]

    def get_function_params(self, name):
        """
        Retrieves the parameters of a given function.
        @param name: The name of the function.
        @return: The parameters of the function.
        """
        return self.get_function_props(name)['params']

    def get_function_body(self, name):
        """
        Retrieves the body of a given function.
        @param name: The name of the function.
        @return: The body AST node of the function.
        """
        return self.get_function_props(name)['body']

    def set_variable(self, name, value):
        """
        Sets the value of a given variable.
        @param name: The name of the variable.
        @param value: The value to set the variable to.
        @raise Exception: If the variable is not found in the table.
        """
        key = (name, 'id')

        if key not in self.__table:
            raise Exception(f"Variable '{name}' not found")
        self.__table[key] = value

    def set_param(self, identifier, param, arg_runtime_value):
        """
        Sets the value of a given parameter for the respective function.
        @param identifier: The name of the function whose parameter is being set.
        @param param: The name of the parameter being set.
        @param arg_runtime_value: The value of the parameter being set.
        @raise Exception: If the function or parameter is not found in the table.
        """
        key = (identifier, 'func')

        if key not in self.__table:
            raise Exception(f"Function '{identifier}' not found")
        self.get_function_params(key)[param] = arg_runtime_value

    def copy(self):
        """
        Creates a copy of the symbol table without the current scope's variables.
        @return: The copy of the symbol table.
        """
        new_table = SymbolTable()
        for key in self.__table.keys():
            if key[1] == 'func':
                new_table.__table[key] = self.__table[key]
        return new_table

    def __str__(self):
        """
        @return: The string representation of the symbol table
        """
        table = ""
        for k, v in sorted(self.__table.items()):
            if k[1] == 'id':
                table += (f"Var: {k[0]}[{k[1]}] =>\n"
                          f"  Value: {v}\n\n")
            elif k[1] == 'func':
                table += (f"Func: {k[0]}[{k[1]}] =>\n"
                          f"  Params: {v['params']}\n"
                          f"  Body: {v['body']}\n\n")
        return table

    def __hash__(self):
        """
        @return: The hash value of the symbol table
        """
        return hash(self.__str__())
