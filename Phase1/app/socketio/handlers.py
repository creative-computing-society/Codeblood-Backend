import json
from socketio import AsyncServer
from app.socketio.socket_map import save_socket, remove_socket, get_all_sockets
from app.db.mongo import nations_col, teams_col
from datetime import datetime

# Load answers once at startup
with open("app/game/answers.json") as f:
    ANSWERS = {entry["nation_id"]: entry["answer"] for entry in json.load(f)}

def register_handlers(sio: AsyncServer):

    @sio.event
    async def connect(sid, environ, auth):
        session_id = auth.get("session_id")
        print("ARI SE BADHA CHUTIYA DOESNT EXIST")
        if not session_id:
            return False  
        print("HARI SE BADHA CHUTIYA DOESNT EXIST1")
        sid = str(sid)
        print("HARI SE BADHA CHUTIYA DOESNT EXIST2")
        session_id = str(session_id)
        print("HARI SE BADHA CHUTIYA DOESNT EXIST3")
        save_socket(session_id, sid)
        print(f"[+] WebSocket connected: {sid} <- session: {session_id}")

    @sio.event
    async def disconnect(sid):
        remove_socket(sid)
        print(f"[-] WebSocket disconnected: {sid}")

    @sio.event
    async def submit_answer(sid, data):
        nation_id = data.get("nation_id")
        submitted_answer = data.get("answer")
        team_name = data.get("team_name")

        if not nation_id or not submitted_answer or not team_name:
            await sio.emit("answer_response", {"status": "invalid_data"}, to=sid)
            return

        correct_answer = ANSWERS.get(nation_id)
        if not correct_answer:
            await sio.emit("answer_response", {"status": "invalid_nation"}, to=sid)
            return

        nation_doc = nations_col.find_one({"_id": nation_id})
        if nation_doc and nation_doc.get("captured"):
            await sio.emit("answer_response", {"status": "already_captured"}, to=sid)
            return

        team_doc = teams_col.find_one({"_id": team_name}) or {"powerups": [], "points": 0, "attempts": []}

        # Get current attempt count for this nation
        attempts_list = team_doc.get("attempts", [])
        nation_attempt = next((a for a in attempts_list if a["nation_id"] == nation_id), None)

        if nation_attempt and nation_attempt["attempt"] >= 3:
            await sio.emit("nation_locked", {"nation_id": nation_id}, to=sid)
            return

        # Answer logic
        if submitted_answer.strip().lower() == correct_answer.lower():
            # Mark as captured
            nations_col.update_one(
                {"_id": nation_id},
                {"$set": {
                    "captured": True,
                    "captured_by": team_name,
                    "timestamp": datetime.utcnow()
                }},
                upsert=True
            )

            # Give points
            teams_col.update_one(
                {"_id": team_name},
                {"$inc": {"points": 100}},
                upsert=True
            )

            await sio.emit("nation_captured", {
                "nation_id": nation_id,
                "captured_by": team_name
            })
            await sio.emit("answer_response", {"status": "correct"}, to=sid)

        else:
            # Update attempts
            updated = False
            for attempt in attempts_list:
                if attempt["nation_id"] == nation_id:
                    attempt["attempt"] += 1
                    updated = True
                    if attempt["attempt"] >= 3:
                        await sio.emit("nation_locked", {"nation_id": nation_id}, to=sid)
                    break
            if not updated:
                attempts_list.append({"nation_id": nation_id, "attempt": 1})

            teams_col.update_one(
                {"_id": team_name},
                {"$set": {"attempts": attempts_list}},
                upsert=True
            )

            await sio.emit("answer_response", {"status": "incorrect"}, to=sid)

    @sio.event
    async def get_nation_status(sid):
        nations = nations_col.find({})
        captured_list = [{
            "nation_id": n["_id"],
            "captured": n.get("captured", False),
            "captured_by": n.get("captured_by")
        } for n in nations]
        await sio.emit("nation_status", captured_list, to=sid)
