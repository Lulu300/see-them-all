from abc import ABC, abstractmethod
from util.video import Video


class Output(ABC):

    @abstractmethod
    def mark_as_watched(videos):
        pass
