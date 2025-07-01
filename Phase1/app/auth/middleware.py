
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.auth.session import validate_session

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            user_id = validate_session(session_id)
            if user_id:
                request.state.user_id = user_id
                return await call_next(request)
        
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)