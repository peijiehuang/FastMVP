class ServiceException(Exception):
    """Business logic exception. Returns HTTP 200 with error code in body."""

    def __init__(self, message: str = "操作失败", code: int = 500):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthException(Exception):
    """Authentication exception. Returns HTTP 401."""

    def __init__(self, message: str = "认证失败"):
        self.message = message
        super().__init__(message)


class ForbiddenException(Exception):
    """Authorization exception. Returns HTTP 403."""

    def __init__(self, message: str = "没有权限"):
        self.message = message
        super().__init__(message)
