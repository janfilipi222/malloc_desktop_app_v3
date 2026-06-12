import ttkbootstrap as ttk
from domain.model.actions.ui_actions import OnJointMove, OnToggleAccMove
import math

class JointAnglePanel(ttk.Frame):
    def __init__(self, parent, on_ui_action, arm_model):
        super().__init__(parent)
        self._on_ui_action = on_ui_action

        # self.config(style="OnSurface.TFrame")

        self._frames = [None for _ in range(6)]
        self._entries = [None for _ in range(6)]
        self._sliders = [None for _ in range(6)]
        self._vals = [None for _ in range(6)]

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._arm_model = arm_model

        self._build_ui()


    def _build_ui(self):

        self.frame = ttk.Labelframe(self, text="Joint Angles", style="Big.TLabelframe")
        self.frame.columnconfigure((0, 1), weight=1)
        self.frame.grid(row=0, column=0, sticky="nsew")

        self.check_btn_val = ttk.BooleanVar(value=False)
        self.acc_check_btn = ttk.Checkbutton(
            self.frame, 
            bootstyle="round-toggle", 
            text="Enable Manual Joint Move", 
            variable=self.check_btn_val,
            command=self._on_toggle_check_btn
            )
        self.acc_check_btn.grid(row=0, column=0, sticky="nsw", padx=20, pady=10)
        
        row_values = (1, 2, 3, 1, 2, 3)
        col_values = (0, 0, 0, 1, 1, 1)

        for i in range(6):
            self._frames[i], self._sliders[i], self._entries[i], self._vals[i] = self._build_slider(
                self.frame, 
                f"J{i+1}", 
                self._arm_model.joints[i].min_angle, 
                self._arm_model.joints[i].max_angle, 
                0.0, 
                i
            )
            self._frames[i].grid(row=row_values[i], column=col_values[i], sticky="nsew", pady=5, padx=10)
            self._sliders[i].config(command=lambda value, id=i: self._on_scale_move(id, value))
        
        for slider in self._sliders:
            slider.state(["disabled"])


    def _on_toggle_check_btn(self):
        value = self.check_btn_val.get()
        self._on_ui_action(OnToggleAccMove(value))
        for slider in self._sliders:
            if value:
                slider.state(["!disabled"])
            else:
                slider.state(["disabled"])


    def _on_scale_move(self, index, value):
        new_value = round(float(value), 2)
        self._entries[index].delete(0, "end")
        self._entries[index].insert(0, new_value)

        # print("slider move:", index)

        self._on_ui_action(OnJointMove(index, math.radians(new_value)))

    def update_joint(self, angle_rad: float, index: int):
        print("updating")
        angle_deg = math.degrees(angle_rad)
        print(angle_deg)
        self._vals[index].set(angle_deg)
        self._sliders[index].set(angle_deg)
        self._entries[index].delete(0, "end")
        self._entries[index].insert(0, angle_deg)

    def update_acc_state(self, state: bool):
        self.check_btn_val.set(state)
        self._on_toggle_check_btn()


    def _build_slider(self, parent, text: str, min: int, max: int, curr: int, index: int):

        frame = ttk.Frame(parent)
        inside_frame = ttk.Frame(frame)
        inside_frame.pack(expand=True)

        label = ttk.Label(inside_frame, text=text, font=("Segoe UI", 12))
        label.pack(side="left")

        entry = ttk.Entry(inside_frame, width=6)
        entry.insert(0, "0.0")
        entry.pack(side="left", padx=10)
        
        slider_frame = ttk.Frame(inside_frame)
        slider_frame.columnconfigure(0, minsize=250)
        slider_frame.rowconfigure(0, weight=1)
        slider_frame.pack(side="left")


        val = ttk.DoubleVar(value=curr)
        def set_var(_):
            value = float(entry.get().strip())
            val.set(value)
            self.master.focus_set()
            self._on_scale_move(index, value)


        slider = ttk.Scale(slider_frame, from_=min, to=max, orient="horizontal", variable=val, length=250)
        slider.grid(row=0, column=0, sticky="nsew", padx=5)

        ttk.Label(slider_frame, text=max).grid(row=1, column=0, sticky="e", padx=5)
        ttk.Label(slider_frame, text=min).grid(row=1, column=0, sticky="w", padx=5)

        entry.bind("<Return>", set_var)

        return frame, slider, entry, val