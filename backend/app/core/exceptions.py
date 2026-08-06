from fastapi import HTTPException, status

class PlatformException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class CredentialsException(PlatformException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status_code.HTTP_401_UNAUTHORIZED,
            detail=detail
        )

class PermissionException(PlatformException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status_code.HTTP_403_FORBIDDEN,
            detail=detail
        )

class NotFoundException(PlatformException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status_code.HTTP_404_NOT_FOUND,
            detail=detail
        )

class SimulationException(PlatformException):
    def __init__(self, detail: str = "Simulation execution failed"):
        super().__init__(
            status_code=status_code.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
