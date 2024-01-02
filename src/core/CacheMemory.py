from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity=1000):
        self.__capacity = capacity
        self.__cache_map = OrderedDict()

    def get(self, key):
        """
        Get the value associated with the provided key
        @param key: The key to retrieve the value of
        @return: The value associated with the provided key
        """
        if key in self.__cache_map:
            # Move to end (Most recently used)
            self.__cache_map.move_to_end(key)
            return self.__cache_map[key]
        return None

    def put(self, key, value):
        """
        Add a new value to the cache, if the key already exists then update the current cached value
        @param key: The key to add to the the cache
        @param value: The value associated with the key to add
        """
        if self.__capacity <= 0:
            return

        if key in self.__cache_map:
            self.__cache_map[key] = value
            self.__cache_map.move_to_end(key)
        else:
            if len(self.__cache_map) >= self.__capacity:
                # Remove least recently used
                self.__cache_map.popitem(last=False)
            self.__cache_map[key] = value

    def has_key(self, key):
        """
        Check if a key exists in the symbol table
        @param key: key to check
        @return: True if the key exists in the symbol, otherwise False
        """
        return key in self.__cache_map

    def display(self):
        print(self.__cache_map)


cache_mem = LRUCache()
