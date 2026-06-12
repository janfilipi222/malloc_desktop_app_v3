import ttkbootstrap as ttk
from domain.model.actions.ui_actions import OnPWMMove

class EeControl(ttk.Frame):
    def __init__(self, parent, on_ui_action):
        super().__init__(parent)

        self._on_ui_action = on_ui_action

        # self.rowconfigure(2, weight=1)
        # self.columnconfigure((0, 1), weight=1)

        self._build_ui()

    def _build_ui(self):

        self.frame = ttk.Labelframe(self, text="EE Control")
        self.frame.pack(fill="both", expand="true")
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand="true", padx=0, pady=(10, 0))


        pwm_frame = self._build_pwm_controller(self)
        pwm_frame.pack(fill="both", expand="true")

        uart_frame, entry, btn = self._build_uart_controller(self)
        uart_frame.pack(fill="both", expand="true")

        self.notebook.add(pwm_frame, text="  PWM  ")
        self.notebook.add(uart_frame, text="  UART  ")


    def _build_pwm_controller(self, parent):
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        
        f1, self.slider_1, self.entry_1 = self._build_slider(frame, "PWM 1", 1000, 2000, curr=1000, index=0)
        f1.grid(row=0, column=0, sticky="new", pady=5)
        self.slider_1.config(command=lambda v: self._handle_pwm_move(index=0, value=float(v)))
        self.entry_1.insert(0, "1000.00")

        f2, self.slider_2, self.entry_2 = self._build_slider(frame, "PWM 2", 28, 97, curr=28, index=1)
        f2.grid(row=1, column=0, sticky="new", pady=5)
        self.slider_2.config(command=lambda v: self._handle_pwm_move(index=1, value=float(v)))
        self.entry_2.insert(0, "28.00")

        return frame
    

    def _handle_pwm_move(self, index: int, value: float):
        new_value = round(float(value), 2)
        
        match(index):
            case 0: 
                self.entry_1.delete(0, "end")
                self.entry_1.insert(0, str(new_value))
            case 1: 
                self.entry_2.delete(0, "end")
                self.entry_2.insert(0, str(new_value))

        self._on_ui_action(OnPWMMove(index, value))


    def _build_uart_controller(self, parent):
        frame = ttk.Frame(parent)
        frame.columnconfigure(0, weight=1)
    
        entry = ttk.Entry(frame, width=15)
        entry.grid(row=0, column=0, sticky="nsew")

        btn = ttk.Button(frame, text="send")
        btn.grid(row=0, column=1, sticky="nsew")


        return frame, entry, btn

        

    def _build_select_btn(self, parent, text: str):
        btn = ttk.Button(parent, text=text, bootstyle="primary")
    
        return btn

    

    def _build_slider(self, parent, text: str, min: int, max: int, curr: int, index: int):
        # frame = ttk.Frame(parent, style="OnSurface.TFrame")
        frame = ttk.Frame(parent)

        frame.columnconfigure(2, weight=1)
        
        label = ttk.Label(frame, text=text, font=("Segoe UI", 10))
        label.grid(row=0, column=0, sticky="ns", padx=5)

        entry = ttk.Entry(frame, width=10)
        entry.grid(row=0, column=1, padx=5) 
        
        slider_frame = ttk.Frame(frame)
        slider_frame.columnconfigure(0, minsize=190)
        slider_frame.rowconfigure(0, weight=1)
        slider_frame.grid(row=0, column=2, sticky="nsew")

        var = ttk.DoubleVar(value=curr)

        def set_var(_):
            value = float(entry.get().strip())
            var.set(value)
            self.master.focus_set()
            self._handle_pwm_move(index, value)


        slider = ttk.Scale(slider_frame, from_=min, to=max, orient="horizontal", variable=var)
        slider.grid(row=0, column=0, sticky="nsew", padx=5)

        ttk.Label(slider_frame, text=max).grid(row=1, column=0, sticky="e", padx=5)

        ttk.Label(slider_frame, text=min).grid(row=1, column=0, sticky="w", padx=5)

        entry.bind("<Return>", set_var)
        

        return frame, slider, entry