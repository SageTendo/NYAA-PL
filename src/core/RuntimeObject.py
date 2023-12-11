class RunTimeObject:
    def __init__(self, label, value, value_type=None):
        self.label = label
        self.value = value
        self.type = value_type

    def copy(self):
        """
        Returns a new instance of the runtime object
        @return: The copy of the provided runtimeobject
        """
        return RunTimeObject(self.label, self.value, self.type)

    def __repr__(self):
        if self.type is None:
            return f"RuntimeObject({self.label}) = {self.value}"
        return f"RuntimeObject({self.label} | {self.type}) = {self.value}"
