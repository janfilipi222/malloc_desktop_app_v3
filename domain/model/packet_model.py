from dataclasses import dataclass

@dataclass(frozen=True)
class PacketModel:
    packet: bytes # actual packet to send
    wait_for_ack: bool = True
    wait_for_done: bool = False
    seq_number: int = 0




