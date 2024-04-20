from app.core.exceptions import CustomException


class EmailExistsException(CustomException):
    code = 400
    error_code = "EMAIL_EXISTS"
    message = "This email already exists"


class InvalidCredentialsException(CustomException):
    code = 401
    error_code = "INVALID_CREDENTIALS"
    message = "Provided credentials is not valid"


class ForgotPasswordTokenException(CustomException):
    code: 400
    error_code = "FORGOT_PASSWORD_TOKEN"
