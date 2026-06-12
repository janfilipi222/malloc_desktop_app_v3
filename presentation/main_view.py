import ttkbootstrap as ttk
from data.serial.connection_state import ConnectionState
from presentation.main_view_model import MainViewModel
from presentation.views.serial_monitor.serial_monitor import SerialMonitor
from presentation.views.manual_control.joint_angle_control import JointAnglePanel
from presentation.views.manual_control.ee_cord_control import EECordControl
from presentation.views.manual_control.ee_control import EeControl
from presentation.views.arm_model_canvas.arm_model_canvas import ArmModelCanvas
from presentation.views.fpp_control.fpp_control import FppControl
from presentation.views.main_control.main_control import MainControl
from domain.model.actions import ui_actions
from domain.model.actions import logic_actions
from queue import Queue
from presentation.views.cv.main_cv_page import MainCVPage

class MainView(ttk.Window):
    def __init__(self, vm: MainViewModel):
        super().__init__(
            title="Malloc Control V3",
            themename="darkly"
            # size=(1400, 800)
        )
        self.state("normal")
        self.state("zoomed")
        # self.resizable(False, False)

        self._vm: MainViewModel = vm

        self._build_ui()

        self._vm.set_on_logic_action(self._handle_logical_action)

        self._update_serial_monitor()


    def _build_ui(self):



        self.ntb = ttk.Notebook(self)
        self.ntb.pack(fill="both", expand=True)
        self.main_tab = ttk.Frame(self.ntb)
        self.cv_tab = ttk.Frame(self.ntb)
        
        self.ntb.add(self.main_tab, text="    Main Control    ")
        self.ntb.add(self.cv_tab, text="    CV    ")

        self.main_tab.columnconfigure((0, 1), weight=1)
        self.main_tab.rowconfigure(0, weight=1)


        # left frame
        self.left_frame = ttk.Frame(self.main_tab)
        self.left_frame.grid(row=0, column=0, sticky="nsew", pady=20, padx=(10, 10))

        self.left_frame.rowconfigure(1, weight=1)

        self.main_control = MainControl(self.main_tab, self._handle_ui_action)
        self.main_control.grid(row=0, column=0, sticky="new", padx=10, pady=10)

        self.serial_monitor = SerialMonitor(self.left_frame, self._handle_ui_action)
        self.serial_monitor.grid(row=1, column=0, sticky="sew")


        # right frame
        self.right_frame = ttk.Frame(self.main_tab)
        self.right_frame.grid(row=0, column=1, sticky="nsew", pady=20, padx=(0, 10))
        self.right_frame.columnconfigure((0, 1), weight=1)
        self.right_frame.rowconfigure(1, weight=1)

        self.joint_angle_panel = JointAnglePanel(self.right_frame, self._handle_ui_action, self._vm.arm_model)
        self.joint_angle_panel.grid(row=0, column=0, sticky="new")

        self.ee_control = EeControl(self.right_frame, self._handle_ui_action)
        self.ee_control.grid(row=0, column=1, sticky="nsew", padx=20)

        # bottom frame
        self.bottom_frame = ttk.Frame(self.right_frame)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(15, 0))

        self.bottom_frame.rowconfigure(0, weight=1)
        self.bottom_frame.columnconfigure((0, 1), weight=1)


        # bottom middle frame
        self.bottom_middle_frame = ttk.Frame(self.bottom_frame)
        self.bottom_middle_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        self.bottom_middle_frame.columnconfigure(0, weight=1)

        self.ee_cord_control = EECordControl(self.bottom_middle_frame, self._handle_ui_action)
        self.ee_cord_control.grid(row=0, column=0, sticky="nsew")

        self.fpp_control = FppControl(self.bottom_middle_frame, self._handle_ui_action)
        self.fpp_control.grid(row=1, column=0, sticky="nsew", pady=(15, 0))

        # test
        self.test_entry = ttk.Entry(self.bottom_middle_frame)
        self.test_entry.insert(0, "5")
        self.test_entry.grid(row=2, column=0, sticky="nw")

        self.test_btn = ttk.Button(self.bottom_middle_frame, text="test btn", command=lambda: self._handle_ui_action(ui_actions.OnTestAction(int(self.test_entry.get()))))
        self.test_btn.grid(row=2, column=0, sticky="ne")

        # bottom right frame
        self.bottom_right_frame = ttk.Frame(self.bottom_frame)
        self.bottom_right_frame.grid(row=0, column=1, sticky="nsew")

        self.bottom_right_frame.columnconfigure(0, weight=1)
        self.bottom_right_frame.rowconfigure(0, weight=1)

        self.model_canvas = ArmModelCanvas(self.bottom_right_frame, self._vm.arm_model)
        self.model_canvas.grid(row=0, column=0, sticky="se")


        # -- cv -- #
        self.main_cv_page = MainCVPage(self.cv_tab, self._handle_ui_action, self._vm)
        self.main_cv_page.pack(expand=True, fill="both")
 


    def _handle_ui_action(self, action: ui_actions.UIAction):
        self._vm.handle_ui_action(action)

    def _handle_logical_action(self, action: logic_actions.LogicAction):
        # print("from view handle logic: ")
        match(action):
            case logic_actions.SetNewPortList():
                self.serial_monitor.update_ports(action.ports)

            case logic_actions.SetNewSerialState():
                self._on_serial_state_change(action.state)
                print(action.state.name)

            case logic_actions.UpdateArmModelCanvas():
                self.model_canvas.update()

            case logic_actions.UpdateEECordValues():
                for i, value in enumerate(action.values):
                    self.ee_cord_control.update_cord(i, value)

            # fpp
            case logic_actions.SetNewPffScriptList():
                self.fpp_control.set_fpp_scripts(action.scripts)
            case logic_actions.OnFppScriptStart():
                self.fpp_control.init_progress(action.size)
                self.fpp_control.set_state("running")
            case logic_actions.OnFppScriptStop():
                self.fpp_control.set_state("stopped")
            case logic_actions.OnFppScriptIndexUpdate():
                self.fpp_control.update_progress(action.curr_index)

            




    def _update_serial_monitor(self):
        # is_available = self._vm.poll_serial_lines()
        # if is_available:
        #     self.serial_monitor.update_log(self._vm.serial_monitor_lines)
        new_lines = self._vm.consume_new_serial_lines()
        if new_lines:
            self.serial_monitor.update_log(new_lines)
        self.after(50, self._update_serial_monitor)


    def _on_serial_state_change(self, state: ConnectionState):
        # print("from main view state:", state.name)
        self.serial_monitor.state_var.set(f"State: {state.name}")
        match(state):
            case ConnectionState.CONNECTED:
                self.serial_monitor.action_btn_var.set("Disconnect")
                new_line = "- CONNECTED -"
            case ConnectionState.DISCONNECTED:
                self.serial_monitor.action_btn_var.set("Connect")
                new_line = "- DISCONNECTED -"
            case ConnectionState.RECONNECTING:
                self.serial_monitor.action_btn_var.set("Stop")
                new_line = "- RECONNECTING -"
            case ConnectionState.STOPPED:
                self.serial_monitor.action_btn_var.set("Connect")
                new_line = "- RECONNECTING STOPPED -"
            
        self.serial_monitor.update_log([new_line])


    
    def run(self):
        print("app run")
        self.mainloop()
