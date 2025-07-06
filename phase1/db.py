from db import get_db

questions = get_db()["questions"]
# question_id
# captured
# captured_by
# timestamp

activity_logs = get_db()["activity_logs"]
# question_id
# captured_by
# timestamp

attempts = get_db()["attempts"]
# team_name
# question_id
# attempts
# solved

bonuses = get_db()["bonuses"]
# team_name
# bonus_question
# extra_points