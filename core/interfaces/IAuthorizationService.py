from abc import ABC, abstractmethod

class IAuthorizationService(ABC):
    @abstractmethod
    def generate_auth_url(self) -> str:
        pass

    @abstractmethod
    def get_access_token(self, code: str) -> str:
        pass
