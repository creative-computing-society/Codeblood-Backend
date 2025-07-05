# from starlette.middleware.sessions import SessionMiddleware

from .routes import router
from .sockets import WebSocketHandler
from .middleware import SessionMiddleware

bundle = {
    "router": router,
    "middleware": SessionMiddleware,
    "socket_handler": WebSocketHandler,
}
