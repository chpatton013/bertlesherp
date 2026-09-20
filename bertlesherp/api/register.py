import uuid

from ._internal import (
    ApiRequestHandler,
    ApiResponse,
    ApiClientError,
    ApiSuccess,
)
from ..app.state import (
    lookup_user,
    lookup_token,
    persist_user,
)


def _generate_token() -> str:
    return uuid.uuid4().hex


class RegisterRequestHandler(ApiRequestHandler):
    @property
    @classmethod
    def error_names(cls):
        return [
            "UNKNOWN_ERROR",
            "USER_TOKEN_MISMATCH",
            "USER_NAME_MISMATCH",
            "USER_NAME_ALRADY_EXISTS",
        ]

    def post(self):
        logging.info("RegisterRequestHandler.post: %s", self.request.body)

        request_name = self.get_body_argument("name")
        request_token = self.get_body_argument("token", default=None)
        user_token = lookup_token(request_name)

        if request_token:
            return self.response(
                self._register_with_name_and_token(
                    request_name, request_token, user_token
                )
            )
        else:
            return self.response(
                self._register_with_name(request_name, user_token)
            )

    def _register_with_name_and_token(
        self, request_name: str, request_token: str, user_token: str
    ) -> ApiResponse:
        if user_token != request_token:
            return ApiClientError(
                status=409,
                name="USER_TOKEN_MISMATCH",
                message=f"User with name '{request_name}' has different token",
            )

        user = lookup_user(request_token)
        if user and user.name != request_name:
            return ApiClientError(
                status=409,
                name="USER_NAME_MISMATCH",
                message=f"User with token '{request_token}' has different name",
            )
        else:
            user = persist_user(request_name, request_token)

        return ApiSuccess(status=200, payload=user.encode())

    def _register_with_name(
        self, request_name: str, user_token: str
    ) -> ApiResponse:
        if user_token:
            return ApiClientError(
                status=409,
                name="USER_NAME_ALREADY_EXISTS",
                message=f"User with name '{request_name}' already exists",
            )

        user = persist_user(request_name, request_token)
        return ApiSuccess(status=200, payload=user.encode())
