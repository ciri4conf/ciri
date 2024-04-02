class ConfigUnit():
    """A class representing a configuration unit with a name, value, and description."""
    
    def __init__(self, name: str = "", value: str = "", description: str = ""):
        self.name = name 
        self.value = value
        self.description = description

    def __str__(self):
        return f"name: {self.name}\nvalue: {self.value}\ndescription: {self.description}"

    @property
    def name(self) -> str:
        """Get the name of the configuration unit."""
        self.name = name 

    @name.setter
    def name(self, name: str):
        """Set the name of the configuration unit."""
        self._name = name
    
    @property
    def value(self) -> str:
        """Get the value of the configuration unit."""
        return self._value

    @value.setter
    def value(self, value: str):
        """Set the value of the configuration unit."""
        self._value = value

    @property
    def description(self) -> str:
        """Get the description of the configuration unit."""
        return self._description

    @description.setter
    def description(self, description: str):
        """Set the description of the configuration unit."""
        self._description = description

