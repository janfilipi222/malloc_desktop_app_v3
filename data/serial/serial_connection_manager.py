
import threading
import time
from .serial_worker import SerialWorker
from .connection_state import ConnectionState
import serial
from typing import Callable


class SerialConnectionManager:
    def __init__(self):
        # self._port = port
        # self._baudrate = baudrate

        self.state = ConnectionState.DISCONNECTED
        self._worker: SerialWorker | None = None
        self._lock = threading.Lock()
        self._reconnect_thread: threading.Thread = None
        self._reconnect_enabled = False

        self._emit_new_state_callback = None
        self._emit_new_msg_callback: Callable[[str], None] = None

    def _set_on_new_msg_callback(self, callback):
        self._emit_new_msg_callback = callback

    def set_new_state_callback(self, new_state_callback):
        self._emit_new_state_callback = new_state_callback

    def set_cannot_connect_callback(self, callback):
        self._on_cannot_connect_callback = callback


    def _set_new_state(self, state):
        self.state = state
        if self._emit_new_state_callback:
            self._emit_new_state_callback(state)

    # manual connect
    def connect(self, port: str, baudrate: int):
        self._port = port
        self._baudrate = baudrate
        with self._lock:
            if (self.state != ConnectionState.DISCONNECTED and
                self.state != ConnectionState.STOPPED):
                return
            
            # self._set_new_state(ConnectionState.CONNECTING)
        
        # print("connecting")
        result = self._try_connect()
        if result:
            # self._set_new_state(ConnectionState.CONNECTED)
            # print("connected")
            pass
        else:
            pass
            # self._set_new_state(ConnectionState.DISCONNECTED)
            # print("cant connect: disconnected")

    def disconnect(self):
        with self._lock:
            if (self.state == ConnectionState.RECONNECTING or 
                self.state == ConnectionState.STOPPED):
                return
            
            self._set_new_state(ConnectionState.DISCONNECTED)
        # print("disconnected")
        self._worker.close()

    def _stop_reconnecting(self):
        self._reconnect_enabled = False
        self._set_new_state(ConnectionState.STOPPED)
        # print("stopped reconnecting")

    # just tries to connect by creating the serial worker
    def _try_connect(self) -> bool:
        try:
            self._worker = SerialWorker(
                self._port, 
                self._baudrate, 
                disconnect_callback=self._handle_sudden_disconnect,
                new_msg_callback=self._emit_new_msg_callback
            )
            self._worker.start()

            with self._lock:
                self._set_new_state(ConnectionState.CONNECTED)
            return True
            
        except serial.SerialException as e:
            self._on_cannot_connect_callback(e)
            return False

    
    # calls when was connected but serial worker suddenly lost the connection
    def _handle_sudden_disconnect(self):
        with self._lock:
            
            if self.state != ConnectionState.CONNECTED:
                return
            self._set_new_state(ConnectionState.RECONNECTING)
            self._reconnect_enabled = True

        # print("starting reconnecting loop")
        self._worker = None
        self._start_reconnecting_loop()

    def _start_reconnecting_loop(self):

        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return
    
        def loop():
            while self._reconnect_enabled:
                # print("trying co connect")
                self._try_connect()
                with self._lock:
                    if self.state == ConnectionState.CONNECTED:
                        # print("from loop: connected")
                        self._reconnect_enabled = False
                        break

                time.sleep(1)
                
        self._reconnect_thread = threading.Thread(
            target=loop, daemon=True
        )
        self._reconnect_thread.start()


    def _stop_worker(self):
        if self._worker:
            self._worker.stop()
            self._worker = None





