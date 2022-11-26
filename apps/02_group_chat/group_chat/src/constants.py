APP_NAME = "GroupChat"
BOT_ADMIN_NAME = "BotBoss"
SERVER_CONNECTIONS: int = 10
SERVER_TYPES = ("server", "client")
SERVER_ENCODING = "UTF-8"

DEFAULT_IP_ADDR = "localIpAddr"


# ---- DOCS


TITLE = """
-----------------------------------------------------------------------------
 __      ___       __           __   __   __        __      __            ___ 
|__) \ /  |  |__| /  \ |\ |    / _` |__) /  \ |  | |__)    /  ` |__|  /\   |  
|     |   |  |  | \__/ | \|    \__> |  \ \__/ \__/ |       \__, |  | /~~\  |                                                                              
-----------------------------------------------------------------------------
"""

USAGE = """
***** USAGE *****
- 1] .--..--..--..--..--..--. USING MAKE FILE .--..--..--..--..--..--.

    Make changes on the MakeFile (modify the PORT, SERVER and HOST Variables on the top 
    according to your needs. If HOST is equal to 'localIpAddr' then the default local 
    ip address will be used

    >>> make up.server <-- Run server first
    >>> make up.client <-- Run a Client instance 

- 2] .--..--..--..--..--..--. CALLING PYTHON SCRIPT .--..--..--..--..--..--.

    >>> python3 -m group_chat server localIpAddr 20020 <-- Run server first
    >>> python3 -m group_chat client localIpAddr 20020 <-- Run a Client instance 

- 3] .--..--..--..--..--..--. SERVER COMMANDS .--..--..--..--..--..--.

    TODO ... 

- 4] .--..--..--..--..--..--. CLIENT COMMANDS .--..--..--..--..--..--.

    TODO ...     
"""