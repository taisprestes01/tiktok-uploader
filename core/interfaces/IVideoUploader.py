from abc import ABC, abstractmethod

class IVideoUploader(ABC):
    @abstractmethod
    def upload(self, access_token: str, title: str = "", privacy_level: str = "SELF_ONLY") -> str:
        pass
    
    @abstractmethod
    def publish(self, access_token: str, publish_id: str, title: str = "", privacy_level: str = "SELF_ONLY") -> dict:
        pass
