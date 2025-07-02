# Code Blood Backend
Welcome to our personal hell.

Here is the structural backdown of what's where
```
.
├── app
│   ├── auth
│   │   ├── middleware.py   # Middleware which gets the Request Header X-SESSION-ID
│   │   ├── routes.py       # /login /auth /logout endpoints
│   │   └── session.py      # interacts with sessions collection
│   ├── db
│   │   └── mongo.py        # has all the collections, import this to access one
│   └── socketio
│       ├── handlers.py     # Socket events for (connect, disconnect)
│       └── socket_map.py
├── config.py               # Configuration for random shit
├── DockerFile
├── main.pyl                # entry_point!()
├── phase1                  # Phase 1 specific code here, this will be turned off when phase1 is over
│   ├── assets
│   │   └── answers.json    # don't get this file leaked
│   └── socketio
│       └── handlers.py     # Socket events for (submit_answer, get_nation_status)
├── README.md               # @self
└── requirements.txt        # pip install -r requirements.txt
```