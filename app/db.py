from db import get_db

db = get_db()["data"]

token_sessions = db["sessions"]
# session_id
# expires_at
# created_at
# user_id
# team_name
# team_id
# team_set

users = db["users"]
# name
# email

socket_connections = db["socket_ids"]
# socket_id
# session_id
# user_id
# team_name
# team_id
# team_set

teams = db["teams"]
# name
# points
# set
# member_count
# members
