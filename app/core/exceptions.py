class CustomException(Exception):
    code = 400
    error_code = "BAD_REQUEST"
    message = "Bad request"

    def __init__(self, message=None) -> None:
        if message:
            self.message = message


class PermissionException(CustomException):
    code = 403
    error_code = "PERMISSION_ERROR"
    message = "Permission error"


class ObjectNotFoundException(CustomException):
    code = 404
    error_code = "OBJECT_NOT_FOUND"
    message = "User is not active"
