from typing import Any, Optional


class RunTimeObject:
    def __init__(
        self, label: str, value: Any, value_type: Optional[str] = None
    ) -> None:
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

    @property
    def type(self) -> Optional[str]:
        """Returns the data type of the runtime object"""
        return self.__type

    def copy(self) -> "RunTimeObject":
        """Returns a new instance of the runtime object"""
        return RunTimeObject(self.__label, self.value, self.type)

    def __repr__(self) -> str:
        """Returns a string representation of the runtime object"""
        if not self.__type:
            return f"RuntimeObject({self.__label}) = {self.value}"
        return f"RuntimeObject({self.__label} | {self.__type}) = {self.__value}"

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
            and self.__type == other.type
        )

    def __hash__(self) -> int:
        """Return the hash of the runtime object"""
        return hash((self.__label, self.__type, self.__value))
