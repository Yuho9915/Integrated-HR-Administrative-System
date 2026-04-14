from app.schemas.common import ApiResponse


def ok(data=None, message: str = 'ok') -> ApiResponse:
    return ApiResponse(success=True, message=message, data=data)
