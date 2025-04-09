from abc import ABC, abstractmethod

class IVideoUploader(ABC):
    @abstractmethod
    def upload(self, access_token: str) -> str:
        pass
