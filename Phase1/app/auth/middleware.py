
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.auth.session import validate_session

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_routes = ["/login", "/auth", "/test"]
        if request.url.path in public_routes:
            return await call_next(request)

        session_id = request.headers.get("X-Session-ID")
        if session_id:
            user_id = validate_session(session_id)
            if user_id:
                request.state.user_id = user_id
                return await call_next(request)
        
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
