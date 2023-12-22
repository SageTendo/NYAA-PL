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
        key = (name, 'id')
        self.__symbol_table[key] = value

    def lookup_variable(self, name, current_scope=False):
        """
        Retrieves the value of a given variable.
        If the current scope flag is not set,
        lookups will be performed on the current scope and all parent scopes
        @param name: The name of the variable.
        @param current_scope: Flag to restrict lookups to the current scope
        @return: The value of the variable.
        @raise Exception: If the variable is not found in the table.
        """
        key = (name, 'id')

        if key in self.__symbol_table:
            return self.__symbol_table[key]

        if not current_scope and self.parent:
            return self.parent.lookup_variable(name)

        raise Exception(f"Variable '{name}' not found in '{self.__name}' scope")

    def insert_function_props(self, name: str, value: dict):
        """
        Adds a function to the symbol table along with its properties.
        @param name: The name of the function.
        @param value: The properties of the function.
        @raise Exception: If the function already exists in the table.
        """
        key = (name, 'func')

        if key in self.__symbol_table:
            raise Exception(f"Function '{name}' already exists")
        self.__symbol_table[key] = value

    def lookup_function_props(self, name, current_scope=False):
        """
        Retrieves the properties of a given function.
        If the current scope flag is not set,
        lookups will be performed on the current scope and all parent scopes
        @param name: The name of the function.
        @param current_scope: Flag to restrict lookups to the current scope
        @return: The properties of the function.
        @raise Exception: If the function is not found in the table.
        """
        key = (name, 'func')

        if key in self.__symbol_table:
            return self.__symbol_table[key]

        if not current_scope and self.parent:
            return self.parent.lookup_function_props(name)

        raise Exception(f"Function '{name}' not found in '{self.__name}' scope")

    def lookup_function_params(self, name):
        """
        Retrieves the parameters of a given function.
        @param name: The name of the function.
        @return: The parameters of the function.
        """
        return self.lookup_function_props(name)['params']

    def lookup_function_body(self, name):
        """
        Retrieves the body of a given function.
        @param name: The name of the function.
        @return: The body AST node of the function.
        """
        return self.lookup_function_props(name)['body']

    def set_variable(self, name, value):
        """
        Sets the value of a given variable.
        @param name: The name of the variable.
        @param value: The value to set the variable to.
        @raise Exception: If the variable is not found in the table.
        """
        key = (name, 'id')

        if key not in self.__symbol_table:
            raise Exception(f"Variable '{name}' not found")
        self.__symbol_table[key] = value

    def set_param(self, identifier, param, arg_runtime_value):
        """
        Sets the value of a given parameter for the respective function.
        @param identifier: The name of the function whose parameter is being set.
        @param param: The name of the parameter being set.
        @param arg_runtime_value: The value of the parameter being set.
        @raise Exception: If the function or parameter is not found in the table.
        """
        key = (identifier, 'func')

        if key not in self.__symbol_table:
            raise Exception(f"Function '{identifier}' not found")
        self.lookup_function_params(key)[param] = arg_runtime_value

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
            if k[1] == 'id':
                table.append(f"Var: {k[0]}[{k[1]}] =>\n"
                             f"  Value: {v}")
            elif k[1] == 'func':
                table.append(f"Func: {k[0]}[{k[1]}] =>\n"
                             f"  Params: {v['params']}\n"
                             f"  Body: {v['body']}")
        return '\n'.join(table)

    def __hash__(self):
        """
        @return: The hash value of the symbol table
        """
        return hash(self.__str__())
