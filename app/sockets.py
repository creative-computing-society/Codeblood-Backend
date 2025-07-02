from typing import Any, Dict, Optional
from logging import getLogger
from socketio import AsyncServer

from app.db_interface import save_socket, remove_socket

logger = getLogger(__name__)


class WebSocketHandler:
    def __init__(
        self,
        sio: AsyncServer,
    ):
        self.sio = sio

        self.sio.on("connect", self.connect)
        self.sio.on("disconnect", self.disconnect)

    @staticmethod
    async def connect(
        sid: str, environ: Dict[str, Any], auth: Optional[Dict[str, Any]]
    ) -> Optional[bool]:
        session_id = auth.get("session_id") if auth else None
        if not session_id:
            return False

        save_socket(session_id, sid)
        print(f"[+] WebSocket connected: {sid} <- session: {session_id}")
        return None

    @staticmethod
    async def disconnect(sid: str) -> None:
        remove_socket(sid)
        print(f"[-] WebSocket disconnected: {sid}")
