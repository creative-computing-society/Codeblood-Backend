from .routes import router
from .middleware import SessionMiddleware
from .sockets import WebSocketHandler

bundle = {
    "router": router,
    "middleware": SessionMiddleware,
    "socket_handler": WebSocketHandler
}