from typing import Any, Dict, Optional
from logging import getLogger
from socketio import AsyncServer

from .db_interface import save_socket, remove_socket, get_session

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
        logger.debug("Socket - Connect")
        session_id = auth.get("session_id") if auth else None
        if not session_id:
            session_id = auth.get("token") if auth else None # My API client can only send auth under the name "token"
        if not session_id:
            return False
        session = get_session(session_id)
        print(session)
        if not session:
            return False

        save_socket(session_id, session, sid)
        logger.debug(f"[+] WebSocket connected: {sid} <- session: {session_id}")
        return True

    @staticmethod
    async def disconnect(sid: str) -> None:
        logger.debug("Socket - Disconect")
        remove_socket(sid)
        logger.debug(f"[-] WebSocket disconnected: {sid}")
