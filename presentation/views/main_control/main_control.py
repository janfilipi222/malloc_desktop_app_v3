import ttkbootstrap as ttk
from domain.model.actions.ui_actions import EnableAllMotors, DisableAllMotors, SetZero, GoToZero



class MainControl(ttk.Labelframe):
    def __init__(self, parent, on_ui_action):
        super().__init__(parent, text="Main Control")

        self._on_ui_action = on_ui_action
        self.columnconfigure(0, weight=1)


        self._build_ui()

    def _build_ui(self):

        self.btn_ena = ttk.Button(self, text="Enable all joints", command= lambda: self._on_ui_action(EnableAllMotors()))
        self.btn_ena.grid(row=0, column=0, sticky="nsew", pady=(15, 5), padx=40)

        self.btn_ena = ttk.Button(self, text="Disable all joints", command= lambda: self._on_ui_action(DisableAllMotors()))
        self.btn_ena.grid(row=1, column=0, sticky="nsew", pady=5, padx=40)

        self.btn_ena = ttk.Button(self, text="Set Zero", command= lambda: self._on_ui_action(SetZero()))
        self.btn_ena.grid(row=2, column=0, sticky="nsew", pady=5, padx=40)

        self.btn_ena = ttk.Button(self, text="Go to Zero pos", command= lambda: self._on_ui_action(GoToZero()))
        self.btn_ena.grid(row=3, column=0, sticky="nsew", pady=5, padx=40)