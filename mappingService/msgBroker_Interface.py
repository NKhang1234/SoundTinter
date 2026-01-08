from abc import ABC, abstractmethod

class MessageBroker(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def send(self, message: str):
        pass

    @abstractmethod
    def get(self):
        pass

    @classmethod
    @abstractmethod
    def close(self):
        pass