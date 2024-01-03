class RunTimeObject:
    def __init__(self, label, value, value_type=None):
        self.__label = label
        self.__value = value
        self.__type = value_type

    @property
    def label(self):
        """
        @return: The label of the runtime object
        """
        return self.__label

    @property
    def value(self):
        """
        @return: The value of the runtime object
        """
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def type(self):
        """
        @return: The type of the runtime object
        """
        return self.__type

    def copy(self):
        """
        Returns a new instance of the runtime object
        @return: The copy of the provided runtimeobject
        """
        return RunTimeObject(self.__label, self.value, self.type)

    def __repr__(self):
        if self.__type is None:
            return f"RuntimeObject({self.__label}) = {self.value}"
        return f"RuntimeObject({self.__label} | {self.__type}) = {self.__value}"

    def __eq__(self, other):
        """
        Checks if the runtime object is equal to another runtimeobject
        @param other: The other runtimeobject to compare with
        @return: True if the runtime objects are equal, false otherwise
        """
        return (isinstance(self, other) and
                self.__label == other.label and
                self.__value == other.label and
                self.__type == other.type)

    def __hash__(self):
        """
        @return: The hash of the runtime object
        """
        return hash((self.__label, self.__type, self.__value))
