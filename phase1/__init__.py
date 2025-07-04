from .sockets import WebSocketHandler
from .routes import router

bundle = {
    "router": router,
    "socket_handler": WebSocketHandler,
}
