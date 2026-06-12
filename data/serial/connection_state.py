from enum import Enum, auto

class ConnectionState(Enum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    CONNECTING = auto()
    RECONNECTING = auto()
    STOPPED = auto()

