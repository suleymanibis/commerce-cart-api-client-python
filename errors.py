class JWTError(Exception):
    pass

class MissingPayload(JWTError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MissingExpirationError(JWTError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TokenExpiredError(JWTError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MissingTokenError(JWTError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ApplicationError(Exception):
    pass

class UnauthorizedError(ApplicationError):
    def __init__(self):
        super().__init__()

class APINotAccessible(ApplicationError):
    def __init__(self):
        super().__init__()