import ttkbootstrap as ttk
from data.serial.connection_state import ConnectionState
from domain.model.actions.ui_actions import *
from collections import deque

class SerialMonitor(ttk.Labelframe):
    def __init__(self, parent, on_ui_action=None):
        super().__init__(parent, padding=5, text="Serial Monitor")

        self._on_ui_action = on_ui_action

        self._curr_state = ConnectionState.DISCONNECTED

        self._autoscroll = True
        self._prev_cmd_index = 0
        self._curr_entry_cmd = ""        
        self._prev_cmds: list[str] = []

        self.curr_lines = deque(maxlen=200)


        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        self._build_ui()


    
    def _build_ui(self):

        self.frame = ttk.Labelframe(self, text="Serial Monitor")

        self._build_top_bar()
        self._build_log()
        self._build_input()


    def _build_top_bar(self):
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        top_frame = ttk.Frame(frame)
        top_frame.pack(fill="x", anchor="n", side="top")

        # Action btn
        self.state_var = ttk.StringVar(value=f"State: {str(self._curr_state.name)}")
        self._connection_label = ttk.Label(top_frame, textvariable=self.state_var)
        self._connection_label.pack(side="left")
        self.action_btn_var = ttk.StringVar(value="Connect")
        self.connect_btn = ttk.Button(
            top_frame, 
            textvariable=self.action_btn_var, 
            bootstyle="primary", 
            command=lambda: self._on_ui_action(OnChangeSerialState(self.action_btn_var.get()))
        )
        self.connect_btn.pack(side="left", padx=5)
        
        # Port
        self._port_btn_var = ttk.StringVar(value="None")
        self._port_btn = ttk.Menubutton(top_frame, textvariable=self._port_btn_var)
        self._port_btn.pack(side="right")
        self._port_btn.bind("<ButtonPress-1>", lambda _: self._on_ui_action(OnPortsUpdate()))
        self._port_menu = ttk.Menu(self._port_btn, tearoff=0)
        self._port_btn["menu"] = self._port_menu

        ttk.Label(top_frame, text="Port:").pack(side="right", padx=5)



        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill="x", anchor="n", side="top", pady=(10, 0))
    
        # Autoscroll
        ttk.Label(bottom_frame, text="Autoscroll:").pack(side="left")
        self.autoscroll_btn = ttk.Button(bottom_frame, text="ON", command=self._toggle_autoscroll)
        self.autoscroll_btn.pack(side="left", padx=(5, 0))

        # Clear
        self.clear_btn = ttk.Button(bottom_frame, text="Clear", command=self._on_clear)
        self.clear_btn.pack(side="left", padx=(50, 0))



    def _build_log(self):
        frame = ttk.Frame(self)
        frame.grid(row=1, column=0, sticky="nsew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.log_text = ttk.Text(
            frame, wrap=None, state="disabled", width=70
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=self.log_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _build_input(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        frame.columnconfigure(0, weight=1)

        placeholder = "Enter message to send:"

        # entry
        self.entry = ttk.Entry(frame)
        self.entry.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.entry.bind("<Return>", lambda _: self._on_send())

        def on_focus_in(e):
            if self.entry.get() == placeholder:
                self.entry.delete(0, "end")
                self.entry.config(foreground="white")
        
        def on_focus_out(e):
            if not self.entry.get():
                self.entry.insert(0, placeholder)
                self.entry.config(foreground="gray")
        
        on_focus_out(None)
        self.entry.bind("<FocusIn>", on_focus_in)
        self.entry.bind("<FocusOut>", on_focus_out)

        self.entry.bind('<Up>', self._on_prev_cmd)
        self.entry.bind('<Down>', self._on_next_cmd)

        # send button
        self.send_btn = ttk.Button(
            frame, text="Send", bootstyle="primary", command=self._on_send
        )
        self.send_btn.grid(row=0, column=1)
    


    
    def set_state(self, state: ConnectionState, btn_text: str):
        self._curr_state = state
        self.state_var.set(value=f"State: {self._curr_state.name}")
        self.action_btn_var.set(btn_text)


    def update_ports(self, ports: list[str]):
        self._port_menu.delete(0, "end")
        self._port_menu.add_command(
            label="None", 
            command=lambda: self._on_port_select("None")
        )
        for port in ports:
            self._port_menu.add_command(
                label=port,
                command=lambda i=port: self._on_port_select(i)
            )
    
    def _on_port_select(self, port: str):
        self._port_btn_var.set(port)
        self._on_ui_action(OnPortSelect(port))




    def _on_prev_cmd(self, _):
        # print("prev")
        if self._prev_cmd_index == -1:
            self._curr_entry_cmd = self.entry.get()

        self._prev_cmd_index += 1
        cmd_count = len(self._prev_cmds) - 1
        # print(cmd_count)
        if self._prev_cmd_index > cmd_count:
            self._prev_cmd_index = cmd_count

        if self._prev_cmd_index > -1:
            self.entry.delete(0, "end")
            self.entry.insert(0, self._prev_cmds[self._prev_cmd_index])
        # print(self._prev_cmd_index)

    def _on_next_cmd(self, _):
        # print("next")
        self._prev_cmd_index -= 1
        if self._prev_cmd_index < -1:
            self._prev_cmd_index = -1

        if self._prev_cmd_index > -1:
            self.entry.delete(0, "end")
            self.entry.insert(0, self._prev_cmds[self._prev_cmd_index])
        else:
            self.entry.delete(0, "end")
            self.entry.insert(0, self._curr_entry_cmd)
        # print(self._prev_cmd_index)


    def _on_clear(self):
        self.curr_lines.clear()
        self._on_ui_action(OnSerialClear())
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disable")

    def _toggle_autoscroll(self):
        if self._autoscroll:
            self.autoscroll_btn.config(text="OFF")
        else:
            self.autoscroll_btn.config(text="ON")
        self._autoscroll = not self._autoscroll


    

    def _on_send(self):
        msg = self.entry.get().strip()
        self.entry.delete(0, "end")
        self._prev_cmd_index = -1

        if self._prev_cmds and not self._prev_cmds[0] == msg:
            # print("inserint")
            self._prev_cmds.insert(0, msg)
        elif not self._prev_cmds:
            # print("inserint 0")
            self._prev_cmds.insert(0, msg)

        self._on_ui_action(OnSerialSend(msg + "\n"))


    def update_log(self, lines):
        if not lines:
            return
        

        self.log_text.config(state="normal")


        for line in lines:
            self.curr_lines.append(line)
            if isinstance(line, str):
                self.log_text.insert("end", line + "\n")
            elif isinstance(line, bytes):
                self.log_text.insert("end", line + b"\n")

        total_lines = int(self.log_text.index("end-1c").split(".")[0])

        if total_lines > self.curr_lines.maxlen:
            lines_to_remove = total_lines - self.curr_lines.maxlen
            self.log_text.delete("1.0", f"{lines_to_remove + 1}.0")
        
        if self._autoscroll:
            self.log_text.see("end")
        self.log_text.config(state="disabled")





