class CommandRegistry:
    """Maps builtin command names to their handler functions.

    Registering here is the single place a new builtin needs to plug in.
    """

    def __init__(self):
        self._commands = {}

    def register(self, name):
        def decorator(func):
            self._commands[name] = func
            return func

        return decorator

    def get(self, name):
        return self._commands.get(name)

    def is_builtin(self, name):
        return name in self._commands

    def names(self):
        return list(self._commands)


registry = CommandRegistry()
