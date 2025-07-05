from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware as Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from .db_interface import get_session

middleware_exceptions = [
    [''],
    ['test'],
    ['login'],
    ['auth']
]

class SessionMiddleware(Starlette):
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, secret_key="nigga")

    async def dispatch(self, request: Request, call_next):
        path = str(request.url).split("/")[3:]
        if path in middleware_exceptions:
            request.state.session = None
            return await call_next(request)

        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            return JSONResponse({"detail": "Unauthorized - No session info provided"}, status_code=401)

        session = get_session(session_id)
        if session is None:
            return JSONResponse({"detail": "Unauthorized - No session found"}, status_code=401)

        request.state.session = session
        return await call_next(request)
