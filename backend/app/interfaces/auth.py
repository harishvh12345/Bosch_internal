from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AuthenticationService(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a clear text password."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify standard password match."""
        pass

    @abstractmethod
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[int] = None) -> str:
        """Generate JWT token string containing user ID and scopes."""
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token payload if valid, returning user claims."""
        pass
