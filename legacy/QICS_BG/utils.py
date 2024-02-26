from abc import abstractmethod


class AbstractObserverUI:
    @abstractmethod
    def update_ui(self, *args, **kwargs):
        pass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
