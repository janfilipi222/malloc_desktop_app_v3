import cv2
import queue
import threading

class CameraService():
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self._running = False
        self._frame_queue = queue.Queue(maxsize=1)


    def start(self):
        self._running = True
        threading.Thread(target=self._loop, daemon=True).start()


    def _loop(self):
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            if not self._frame_queue.full():
                self._frame_queue.put(frame)
            else:
                self._frame_queue.get_nowait()
                self._frame_queue.put(frame)
        
    def get_frame(self):
        try:
            return self._frame_queue.get_nowait()
        except queue.Empty:
            return None
        
    def pause(self):
        self._running = False
        

    def stop(self):
        self._running = False
        self.cap.release()

