import ttkbootstrap as ttk
import math
from domain.model.actions.ui_actions import OnEECordMove, OnGoCordButton



class EECordControl(ttk.Frame):
    
    def __init__(self, parent, on_ui_action):
        super().__init__(parent)
        self._on_ui_action = on_ui_action


        self.columnconfigure((0, 1), weight=1)

        self._entries = [None for _ in range(6)]
        self._frames = [None for _ in range(6)]

        self._build_ui()


    def _build_ui(self):
        
        self.frame = ttk.Labelframe(self, text="EE Position")
        self.frame.columnconfigure((0, 1, 2), weight=1)
        self.frame.pack(expand="true", fill="both")

        pad_top = 15
        pad_bot = 15

        row_values = (2, 2, 2, 3, 3, 3)
        col_values = (0, 1, 2, 0, 1, 2)
        text_values = ("X", "Y", "Z", "RX", "RY", "RZ")

        spacer_top = ttk.Frame(self.frame, height=10)
        spacer_top.grid(row=0, column=0, columnspan=2)

        for i in range(6):
                
            entry = CordEntry(self.frame, text_values[i], self._on_change, i)
            self._entries[i] = entry
            if (i < 3):
                entry.grid(row=1, column=i, sticky="nse", padx=10, pady=10)
            else:
                entry.grid(row=2, column=i - 3, sticky="nse", padx=10, pady=10)

        spacer_bot = ttk.Frame(self.frame, height=10)
        spacer_bot.grid(row=4, column=0, columnspan=2)

        bottom_frame = ttk.Frame(self.frame)
        bottom_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

        self.go_btn = ttk.Button(bottom_frame, text="Go", command=self._on_go_btn)
        self.go_btn.pack(side="right", fill="y")

        self.time_entry = ttk.Entry(bottom_frame, font=("Segoe UI", 8), width=6)
        self.time_entry.pack(side="right", padx=(5, 20), anchor="center")
        self.time_entry.insert(0, "1000")

        ttk.Label(bottom_frame, text="time (ms):").pack(side="right", anchor="center")


    def _on_go_btn(self):
        self._on_ui_action(OnGoCordButton(float(self.time_entry.get().strip())))

    def _on_change(self, index: int, value: float):
        # print(index, value)
        self._on_ui_action(OnEECordMove(index, value))


    def update_cord(self, index: int, value: float):

        if index < 3:
            e: CordEntry = self._entries[index]
            e.update_value(round(value, 2))
        else:
            e: CordEntry = self._entries[index]
            e.update_value(round(math.degrees(value), 2))

            


class CordEntry(ttk.Frame):
    def __init__(self, parent, text: str, on_change, index: int, increment_step = 10):
        super().__init__(parent)
        self._on_change = on_change
        self._text = text

        self.columnconfigure(2, weight=1)
        self.increment_step = increment_step
        self._index = index

        self._build_ui()

    def _build_ui(self):

        
        ttk.Label(self, text=self._text, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="ns", padx=(0, 10))

        self._decrement_btn = ttk.Button(self, text="-", command=self._decrement)
        self._decrement_btn.grid(row=0, column=1, sticky="ns")

        self.entry = ttk.Entry(self, width=7)
        self.entry.grid(row=0, column=2)
        self.entry.insert(0, "0.00")
        self.entry.bind("<Return>", self._entry_enter)

        self._increment_btn = ttk.Button(self, text="+", command=self._increment)
        self._increment_btn.grid(row=0, column=3, sticky="ns")

    def _entry_enter(self, _):
        self._on_change(self._index, float(self.entry.get().strip()))
        self.master.focus_set()

    def _increment(self):
        value = float(self.entry.get().strip()) + self.increment_step
        self.entry.delete(0, "end")
        self.entry.insert(0, str(round(value, 2)))
        self._on_change(self._index, value)

    def _decrement(self):
        value = float(self.entry.get().strip()) - self.increment_step
        self.entry.delete(0, "end")
        self.entry.insert(0, str(round(value, 2)))
        self._on_change(self._index, value)


    def update_value(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
