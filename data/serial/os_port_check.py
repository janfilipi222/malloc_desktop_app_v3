import serial.tools.list_ports


def is_port_present(port_name: str) -> bool:
    for p in serial.tools.list_ports.comports():
        if p.device == port_name:
            return True
    return False
