class AComponent:
    def __init__(self):
        self.__debug_mode = False

    def debug(self, debug_arg):
        if self.__debug_mode:
            print(debug_arg)

    def verbose(self, debug_mode=False):
        self.__debug_mode = debug_mode
