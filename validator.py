from app.registeration.models import TeamDashboard

test_data = {
    "team_code": "YeNNiI11",
    "players": [
        {
            "name": "hari",
            "email": "sri21harisesh@gmail.com",
            "id": "a97d1e4a-fcf8-5943-aba2-c2dd19f50d1a",
            "is_wizard": False,
            "is_hacker": True
        },
        {
            "name": "dsdfsdfsdf",
            "email": "jsriharisesh_be24@thapar.edu",
            "id": "890e7504-37de-56f6-aace-7966e1cc718d",
            "is_wizard": True,
            "is_hacker": False
        }
    ]
}

validated_data = TeamDashboard(**test_data)
print(validated_data)