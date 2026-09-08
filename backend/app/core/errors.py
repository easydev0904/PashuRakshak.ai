"""Domain exceptions and friendly-message mapping.

Handlers registered in app.main translate these into a consistent JSON
error shape and make sure no raw exception detail ever reaches the client.
"""

from typing import Optional


class AppError(Exception):
    status_code = 400
    default_message = "Something went wrong. Please try again."

    def __init__(self, message: Optional[str] = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class NotFoundError(AppError):
    status_code = 404
    default_message = "The requested item could not be found."


class ValidationAppError(AppError):
    status_code = 422
    default_message = "Some of the information provided is not valid."


class AuthenticationError(AppError):
    status_code = 401
    default_message = "Could not verify your credentials. Please log in again."


class AuthorizationError(AppError):
    status_code = 403
    default_message = "You do not have permission to do that."


class ConflictError(AppError):
    status_code = 409
    default_message = "This action conflicts with existing data."
