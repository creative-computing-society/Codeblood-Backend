from ..db.mongo import sockets_col

def save_socket(session_id: str, socket_id: str):
    sockets_col.update_one(
        {"_id": socket_id},
        {"$set": {"session_id": session_id}},
        upsert=True
    )

def remove_socket(socket_id: str):
    sockets_col.delete_one({"_id": socket_id})

def get_all_sockets() -> list[str]:
    return [doc["_id"] for doc in sockets_col.find({})]
