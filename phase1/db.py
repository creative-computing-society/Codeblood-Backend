from db import get_db

nations = get_db()["nations"]
activity_logs = get_db()["activity_logs"]
attempts = get_db()["attempts"]
