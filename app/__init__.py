from .routes import router
from .sockets import WebSocketHandler
from starlette.middleware.sessions import SessionMiddleware

bundle = {
    "router": router,
    "middleware": SessionMiddleware,
    "socket_handler": WebSocketHandler,
}
