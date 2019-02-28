from abc import ABC, abstractmethod


class Input(ABC):

    @abstractmethod
    def recently_watched(self):
        pass
