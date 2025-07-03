from starlette.middleware import sessions
from starlette.requests import Request
from starlette.responses import JSONResponse

from .db_interface import validate_session


# class SessionMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         session_id = request.headers.get("X-Session-ID")
#         if not session_id:
#             return JSONResponse({"detail": "Unauthorized"}, status_code=401)
#
#         user_id = validate_session(session_id)
#         if not user_id:
#             return JSONResponse({"detail": "Unauthorized"}, status_code=401)
#
#         request.state.user_id = user_id
#         return await call_next(request)
#


class SessionMiddleware(sessions.SessionMiddleware):
    def __init__(self) -> None:
        super().__init__(secret_key="yourmom")
