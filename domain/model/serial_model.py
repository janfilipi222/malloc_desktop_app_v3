from dataclasses import dataclass

@dataclass
class SerialModel:
    port: str
    baudrate: int = 115200

