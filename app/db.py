from db import get_db

db = get_db()["data"]
token_sessions = db["sessions"]
users = db["users"]
socket_connections = db["socket_ids"]
teams = db["teams"]
