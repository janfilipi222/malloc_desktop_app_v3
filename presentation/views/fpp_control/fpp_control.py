import ttkbootstrap as ttk
from domain.model.actions.ui_actions import RunFppScript, StopFppScript, UniBtnPressed, UpdateFppScriptList



class FppControl(ttk.Labelframe):
    def __init__(self, parent, on_ui_action):
        super().__init__(parent, text="Fpp Script Control")

        self._on_ui_action = on_ui_action
        self.columnconfigure(0, weight=1)

        self._script_list: list[str] = []

        self._build_ui()

    def _build_ui(self):
        
        # top main part
        self.frame_top = ttk.Frame(self)
        self.frame_top.grid(row=0, column=0, sticky="new")
        
        ttk.Label(self.frame_top, text="File Name:").pack(side="left", padx=(10, 2))

        self.combo = ttk.Combobox(
            self.frame_top,
            state="normal"
        )
        self.combo.pack(side="left", fill="x", padx=(0, 15), pady=10, expand=True)

        self.combo.bind("<Escape>", lambda _: self.focus_set())
        self.combo.bind("<Button-1>", lambda _: self._load_scripts())

        # self.entry = ttk.Entry(self.frame_top)
        # self.entry.insert(0, "fpp_test")  # inserts default code
        # self.entry.pack(side="left", fill="x", padx=(0, 15), pady=10, expand=True)

        self.run_btn = ttk.Button(self.frame_top, text="Run Fpp", command=self._on_run_btn)
        self.run_btn.pack(side="right", pady=10, padx=10)

        self.stop_btn = ttk.Button(self.frame_top, text="Stop", command=lambda: self._on_ui_action(StopFppScript()))
        self.stop_btn.pack(side="right")


        # frame middle with uni btns
        self.frame_btn = ttk.Frame(self)
        self.frame_btn.grid(row=1, column=0, sticky="new", pady=(5, 10))

        self.uni_btns: list[ttk.Button] = []
        for i in range(3):
            btn = ttk.Button(self.frame_btn, text=f"btn {i}", command=lambda i=i: self._on_uni_btn_press(i))
            btn.pack(side="left", padx=10)
            self.uni_btns.append(btn)



        # frame btn with load bar
        self.frame_bot = ttk.Frame(self)
        self.frame_bot.grid(row=2, column=0, sticky="new", pady=(5, 10))

        self.state_label = ttk.Label(self.frame_bot, text="State: stopped", font=("Segoe UI", 10))
        self.state_label.pack(side="left", padx=(10, 10))

        self.progress_label = ttk.Label(self.frame_bot, text="instr: 0", font=("Segoe UI", 10))
        self.progress_label.pack(side="left", padx=10)

        self.progress = ttk.Progressbar(self.frame_bot)
        self.progress.pack(side="right", expand=True, fill="both", padx=(0, 10))

    def _load_scripts(self):
        self._on_ui_action(UpdateFppScriptList())

    def set_fpp_scripts(self, scripts: list[str]):
        self._script_list = scripts
        self.combo.config(values=self._script_list)

    def _on_uni_btn_press(self, i: int):
        # print("uni btn:", i)
        # print(type(i))
        self._on_ui_action(UniBtnPressed(i))

    def _on_run_btn(self):
        file_name = self.combo.get().strip()
        self._on_ui_action(RunFppScript(file_name))

    
    def init_progress(self, max: int):
        self.progress["maximum"] = max
        self.progress["value"] = 0
        self.update_idletasks()
        self.update()

    def set_state(self, state: str):
        self.state_label.config(text=f"State: {state}")
        if state == "stopped":
            self.update_progress(0)
        self.update_idletasks()
        self.update()

    def update_progress(self, value: int):
        self.progress["value"] = value

        self.progress_label.config(text=f"instr: {value}")
        self.update_idletasks()
        self.update()
    

    
    # def _on_run_btn(self):
    #     file_name = self.entry.get().strip()
    #     # Spouštíme akci, která může běžet na pozadí
    #     self._on_ui_action(RunFppScript(file_name))
    
    # def init_progress(self, max: int):
    #     print("progress init")
    #     self.progress["maximum"] = max
    #     self.progress["value"] = 0
    
    # def set_state(self, state: str):
    # # Bezpečné UI update i z jiného threadu
    #     print("state set to", state)
    #     self.after(0, lambda: self.state_label.config(text=f"State: {state}"))

    # def update_progress(self, value: int):
    #     print("update progress to", value)
    #     # Bezpečné UI update i z jiného threadu
    #     def _update():
    #         self.progress["value"] = value
    #         self.progress_label.config(text=f"instr: {value}")
    #     self.after(0, _update)





