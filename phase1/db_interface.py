from datetime import datetime
from .db import nations

# Nations
def get_nation_via_id(nation_id: str):
    return nations.find_one({"_id": nation_id})

def capture_nation(nation_id: str, capturer_team_name: str):
    nations.update_one(
        {"_id": nation_id},
        {
            "$set": {
                "captured": True,
                "captured_by": capturer_team_name,
                "timestamp": datetime.now(),
            }
        },
        upsert=True,
    )

def get_all_nations():
    return nations.find({})