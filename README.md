# Code Blood Backend
Welcome to our personal hell.

Here is the structural backdown of what's where
```
.
├── main.py               # entry_point!()
├── config.py             # App configuration
├── DockerFile
├── README.md             # @self
├── requirements.txt      # pip install -r requirements.txt
├── app                   # App - Stuff for basic user functionality
│   ├── __init__.py       # App Bundler
│   ├── middleware.py     # HTTP Middlewares
│   ├── routes.py         # HTTP handlers
│   ├── sockets.py        # Handler of socket events
│   ├── db.py             # Collections of the phase
│   └── db_interface.py   # Functions which expose the db collections
└── phase1
    ├── __init__.py       # Phase 1 Bundler
    ├── db.py
    ├── db_interface.py
    ├── sockets.py
    └── assets
        └── answers.json  # TOP SECRET

```

# Todo
- Track question attempts
- Point system

# Conditionality
## App (For All)
### HTTP Request
- /login
- /auth
- /logout
### DB Collections
- Team
- User
- SocketId (For socket_id <--> user_id relation for an active connection)
- Sessions (For tokens and shit)
### Socket Request
NONE

## Phase 0 (Joining)
### HTTP Request
- /register (User registeration)
- /team_create (Team registeration)
- /join_team
### DB Collection
### HTTP Request
- /leaderboard
### DB Collections
### Socket Requests
NONE
### Socket Request
NONE

## Phase 1 (Game 1)
### HTTP Request
### DB Collections
- Nation
- Activity Log
### Socket Request
- submit_answer
- get_nation_status

## Phase 2 (Game 2)
### HTTP Request
### DB Collections
### Socket Request

## Phase 3 (Game 3)
### HTTP Request
### DB Collections
### Socket Request

## Phase 4 (After game)
### HTTP Request
- /leaderboard
### DB Collections
### Socket Request