# Code Blood Backend
Welcome to our personal hell.

Here is the structural backdown of what's where
```
.
├── main.py                 # entry_point!()
├── config.py               # Configuration for random shit
├── DockerFile
├── README.md               # @self
└── requirements.txt        # pip install -r requirements.txt
│
├── app                     # Code with basic neccessities
│   ├── auth
│   │   ├── middleware.py   # Middleware which gets the Request Header X-SESSION-ID
│   │   ├── routes.py       # /login /auth /logout endpoints
│   │   └── session.py      # interacts with sessions collection
│   ├── db
│   │   └── mongo.py        # has all the collections, import this to access one
│   └── socketio
│       ├── handlers.py     # Socket events for (connect, disconnect)
│       └── socket_map.py
│
├── phase1                  # Phase 1 specific code here, this will be turned off when phase1 is over
│   ├── assets
│   │   └── answers.json    # don't get this file leaked
│   └── socketio
│       └── handlers.py     # Socket events for (submit_answer, get_nation_status)
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