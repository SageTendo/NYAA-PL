from typing import Any


class RunTimeObject:
    def __init__(self, label: str, value: Any, value_type=None):
        """
        Initializes a new runtime object
        @param label: The label of the runtime object
        @param value: The value held by the runtime object
        @param value_type: The data type of the runtime object (default: None if not provided)
        """
        self.__label = label
        self.__value = value
        self.__type = value_type

    @property
    def label(self):
        """Returns the label of the runtime object"""
        return self.__label

    @property
    def value(self):
        """Returns the value held by the runtime object"""
        return self.__value

    @value.setter
    def value(self, value):
        """Set the value of the runtime object"""
        self.__value = value

    @property
    def type(self):
        """Returns the data type of the runtime object"""
        return self.__type

    def copy(self):
        """Returns a new instance of the runtime object"""
        return RunTimeObject(self.__label, self.value, self.type)

    def __repr__(self):
        """Returns a string representation of the runtime object"""
        if self.__type is None:
            return f"RuntimeObject({self.__label}) = {self.value}"
        return f"RuntimeObject({self.__label} | {self.__type}) = {self.__value}"

    def __eq__(self, other):
        """
        Checks if the runtime object is equal to another runtimeobject
        @param other: The other runtimeobject to compare with
        @return: True if the runtime objects are equal, false otherwise
        """
        return (
            isinstance(self, other)
            and self.__label == other.label
            and self.__value == other.label
            and self.__type == other.type
        )

    def __hash__(self):
        """Return the hash of the runtime object"""
        return hash((self.__label, self.__type, self.__value))
