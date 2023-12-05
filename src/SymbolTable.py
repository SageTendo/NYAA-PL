class SymbolTable:
    def __init__(self):
        self.table = {}

    def add_identifier(self, name: str, value: 'RunTimeObject'):
        key = (name, 'id')
        self.table[key] = value

    def get_identifier(self, name):
        key = (name, 'id')

        if key not in self.table:
            raise Exception(f"Identifier '{name}' not found")
        return self.table[key]

    def add_function_props(self, name: str, value: dict):
        key = (name, 'func')

        if key in self.table:
            raise Exception(f"Function '{name}' already exists")
        self.table[key] = value

    def get_function_props(self, name):
        key = (name, 'func')

        if key not in self.table:
            raise Exception(f"Function '{name}' not found")
        return self.table[key]

    def get_function_params(self, name):
        return self.get_function_props(name)['params']

    def get_function_body(self, name):
        return self.get_function_props(name)['body']

    def set_identifier(self, name, value):
        key = (name, 'id')

        if key not in self.table:
            raise Exception(f"Identifier '{name}' not found")
        self.table[key] = value

    def set_param(self, identifier, param, arg_runtime_value):
        key = (identifier, 'func')

        if key not in self.table:
            raise Exception(f"Function '{identifier}' not found")
        self.get_function_params(key)[param] = arg_runtime_value

    def copy(self):
        new_table = SymbolTable()
        for key in self.table.keys():
            if key[1] == 'func':
                new_table.table[key] = self.table[key]
        return new_table
