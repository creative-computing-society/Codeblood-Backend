from pydantic import BaseModel

class SocketMap(BaseModel):
    socket_id: str
    session_id: str