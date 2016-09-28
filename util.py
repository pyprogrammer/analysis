import atexit
import os
import pickle

class PersistentVariable(object):
    __variables = {}
    __loaded = False
    __persistence_name = "persist.pickle"
    __store_registered = False

    def __init__(self, name):
        self.name = name

    @property
    def value(self):
        if not self.__loaded:
            PersistentVariable._load_variables()
        return self.__variables[self.name]

    @value.setter
    def value(self, val):
        if not self.__loaded:
            PersistentVariable._load_variables()

        self.__variables[self.name] = val

        if not self.__store_registered:
            self.__store_registered = True
            atexit.register(PersistentVariable._store)

    @classmethod
    def _load_variables(cls):
        cls.__loaded = True
        try:
            with open(cls.__persistence_name) as loadfile:
                cls.__variables = pickle.load(loadfile)
        except IOError:
            pass

    @classmethod
    def _store(cls):
        with open(cls.__persistence_name, "w") as loadfile:
            pickle.dump(cls.__variables, loadfile)

    @classmethod
    def clear(cls):
        try:
            os.remove(cls.__persistence_name)
        except OSError:
            pass