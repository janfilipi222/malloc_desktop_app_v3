from .serial_connection_manager import SerialConnectionManager
from .os_port_provider import OSPortProvider
from typing import Callable

class SerialClient:
    def __init__(self, connection_manager: SerialConnectionManager):
        self._manager: SerialConnectionManager = connection_manager
        self._manager._set_on_new_msg_callback(self._on_new_msg)

        self._listeners: list[Callable[[str], None]] = []


    def subscribe(self, fn: Callable[[str], None]):
        self._listeners.append(fn)
    

    def _on_new_msg(self, msg: str):
        # print("new msg from client: " + msg)
        for fn in self._listeners:
            fn(msg)



    def connect(self, port: str, baudrate: int):
        self._manager.connect(port, baudrate)

    def disconnect(self):
        self._manager.disconnect()

    def stop_reconnecting(self):
        self._manager._stop_reconnecting()

    def send(self, msg: bytes):
        try:
            self._manager._worker.send(msg)
        except AttributeError:
            self._on_send_error_callback()

    def new_msg(self):
        pass

    def get_port_list(self) -> list[str]:
        return OSPortProvider.list_ports()

    def get_state(self):
        return self._manager.state

    # def poll_lines(self) -> list[str]:
    #     # print("client poll")
    #     if not self._manager._worker:
    #         return []
    #     lines = []
    #     while not self._manager._worker._recv_queue.empty():
    #         lines.append(self._manager._worker._recv_queue.get())
    #     return lines



    
    def set_new_state_callback(self, callback):
        self._manager.set_new_state_callback(callback)

    def set_cannot_connect_callback(self, callback):
        self._manager.set_cannot_connect_callback(callback)

    def set_send_error_callback(self, callback):
        self._on_send_error_callback = callback

