from abc import ABC, abstractmethod


class Output(ABC):

    @abstractmethod
    def mark_as_watched(episodes):
        pass
