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

    def __eq__(self, other):
        """
        Checks if the runtime object is equal to another runtimeobject
        @param other: The other runtimeobject to compare with
        @return: True if the runtime objects are equal, false otherwise
        """
        return (isinstance(self, other) and
                self.label == other.label and
                self.value == other.label and
                self.type == other.type)

    def __hash__(self):
        """
        @return: The hash of the runtime object
        """
        return hash((self.label, self.type, self.value))
