from typing import Any


class RunTimeObject:
    def __init__(self, label: str, value: Any) -> None:
        """
        Initializes a new runtime object
        @param label: The label of the runtime object
        @param value: The value held by the runtime object
        """
        self.__label = label
        self.__value = value

    @property
    def label(self) -> str:
        """Returns the label of the runtime object"""
        return self.__label

    @property
    def value(self) -> Any:
        """Returns the value held by the runtime object"""
        return self.__value

    @value.setter
    def value(self, value: Any) -> None:
        """Set the value of the runtime object"""
        self.__value = value

    def copy(self) -> "RunTimeObject":
        """Returns a new instance of the runtime object"""
        return RunTimeObject(self.__label, self.value)

    def __repr__(self) -> str:
        """Returns a string representation of the runtime object"""
        return f"RuntimeObject({self.__label}) = {self.value}"

    def __eq__(self, other) -> bool:
        """
        Checks if the runtime object is equal to another runtime object
        @param other: The other runtime object to compare with
        @return: True if the runtime objects are equal, false otherwise
        """
        return (
            isinstance(self, other)
            and self.__label == other.label
            and self.__value == other.label
        )

    def __hash__(self) -> int:
        """Return the hash of the runtime object"""
        return hash((self.__label, self.__value))
