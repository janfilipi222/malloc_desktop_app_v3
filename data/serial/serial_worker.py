import time
import queue
import serial
import threading
from .connection_state import ConnectionState
from .os_port_check import is_port_present

# import serial.tools.list_ports


class SerialWorker(threading.Thread):
    def __init__(self, port: str, baudrate: int, disconnect_callback=None, new_msg_callback=None):
        super().__init__(daemon=True)
        self._serial: serial.Serial | None = None
        self._port: str = port
        self._baudrate: int = baudrate
        self._send_queue = queue.Queue()
        self._recv_queue = queue.Queue()
        self._disconnect_callback = disconnect_callback
        self._new_msg_callback = new_msg_callback
        self._running = True

        self._last_port_check = 0.0
        self._port_check_interval = 1.0

        self._serial = serial.Serial(port=self._port, baudrate=self._baudrate, timeout=0.1)
        # self.open()

    def open(self):
        self._serial = serial.Serial(port=self._port, baudrate=self._baudrate, timeout=0.1)

    def close(self):
        self._running = False
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None

    def is_open(self):
        return self._serial is not None and self._serial.is_open


    def run(self):
        while self._running:
            self._recv_loop()
            self._send_loop()
            self._check_idle()
            time.sleep(0.001)
            

    def _recv_loop(self):
        try:
            if self._serial.in_waiting:
                # line = self._serial.readline().decode(errors="ignore").strip()
                line = self._serial.readline().strip()
                # self._recv_queue.put(line)
                self._new_msg_callback(line)
                # print("from worker new line: ", line)
        except serial.SerialException:
            pass
            # self._disconnect_callback()

    def _send_loop(self):
        try:
            msg = self._send_queue.get_nowait()
            self._serial.write(msg)
        except queue.Empty:
            pass


    def send(self, msg: bytes):
        # print("in worker send msg: ", msg)
        self._send_queue.put(msg)

    def _check_idle(self):
        self._ensure_port_alive()



    def _trigger_disconnect(self):
        # print("serial worker sudden disconnect")
        if self._disconnect_callback:
            self._disconnect_callback()


    def _ensure_port_alive(self):

        now = time.monotonic()
        if now < self._last_port_check + self._port_check_interval:
            return
        
        self._last_port_check = now

        if not is_port_present(self._port):
            self.close()
            self._trigger_disconnect()
        


    def stop(self):
        pass

