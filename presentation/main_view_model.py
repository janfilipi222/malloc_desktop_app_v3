from data.serial.serial_client import SerialClient
from domain.communication.command_client import CommandClient
from domain.model.actions import ui_actions
from domain.model.actions import logic_actions
from domain.model.actions import master_action
from domain.model.actions import slave_action
from domain.model.serial_model import SerialModel
from data.serial.connection_state import ConnectionState
from collections import deque
from domain.model.arm_model import ArmModel
from domain.model.arm_model import Vertex
from typing import Callable
from domain.motion import FK
from copy import deepcopy
import math
from app.app_context import AppContext
from domain.gcode.gcode_loader import GCodeLoader
from domain.gcode.gcode_parser import GCodeParser
from domain.gcode.file_list_provider import FileListProvider
from domain.camera.camera_service import CameraService
from domain.camera.manual_brightness_detector import ManualBrightnessDetector

class MainViewModel:
    def __init__(
            self, 
            serial_client: SerialClient, 
            command_client: CommandClient, 
            context: AppContext,
            gcode_loader,
            gcode_parser,
            camera_service: CameraService,
            detector: ManualBrightnessDetector
            ):

        self._context: AppContext = context
        self.arm_model = ArmModel()
        self.loader: GCodeLoader = gcode_loader
        self.parser: GCodeParser = gcode_parser
        self._camera_service: CameraService = camera_service
        self._detector: ManualBrightnessDetector = detector
        
        self._ser_client = serial_client
        self._ser_client.set_new_state_callback(self.on_state_change_callback)
        self._ser_client.set_send_error_callback(self._handle_send_error_callback)
        self._ser_client.set_cannot_connect_callback(self._handle_cannot_connect_callback)
        self._ser_client.subscribe(self._handle_new_serial_msg)
        self._new_serial_lines = deque()

        self._com_client = command_client
        self._com_client.subscribe_slave_action(self._handle_on_slave_action)
        self._com_client.hardware_model = self.arm_model.hardware

        # self._new_monitor_msg = False
        self._fire_logic_action: Callable[[logic_actions.LogicAction], None] | None = None
        self._serial_model = SerialModel(port="None")

        self._com_client.joints = self.arm_model.joints
        self._com_client.hardware = self.arm_model.hardware

        # cv
        self.offset_x0 = 47
        self.offset_x1 = 571
        self.offset_y0 = 66
        self.offset_y1 = 418


    def handle_ui_action(self, action: ui_actions.UIAction):
        match (action):
            case ui_actions.OnPortSelect():
                # print("port select", action.port)
                self._serial_model.port = action.port

            case ui_actions.OnPortsUpdate():
                self._send_logic_action(logic_actions.SetNewPortList(self._ser_client.get_port_list()))

            case ui_actions.OnSerialSend():
                # print("on serial send", action.msg)
                self._ser_client.send(action.msg.encode("ascii"))

            case ui_actions.OnChangeSerialState():
                self._handle_on_change_serial_state(action.btn_text)

            case ui_actions.OnSerialClear():
                self._new_serial_lines.clear()
                # print("vm: on clear")

            case ui_actions.OnJointMove():
                self._handle_on_joint_move(action.index, action.value)

            case ui_actions.OnEECordMove():
                self._handle_on_EE_cord_move(action.index, action.value)
            
            case ui_actions.OnPWMMove():
                self._com_client.set_master_action(master_action.OnPWMMove(action.index, action.value))

            case ui_actions.OnToggleAccMove():
                self._com_client.set_master_action(master_action.OnSetAccMovement(action.state))

            case ui_actions.OnGoCordButton():
                x, y, z = self.arm_model.target_ee_position.pos
                pitch = self.arm_model.target_ee_position.rot[0]
                self._com_client.set_master_action(master_action.On4DoFMove(x, y, z, pitch, action.time))

            # FPP
            case ui_actions.UpdateFppScriptList():
                scripts = FileListProvider.list_files(self._context.fpp_dir)
                self._send_logic_action(logic_actions.SetNewPffScriptList(scripts))

            case ui_actions.RunFppScript():
                self._run_fpp_script(action.file_name)

            case ui_actions.StopFppScript():
                self._com_client.set_master_action(master_action.StopFppRunning())
                print("stop")

            case ui_actions.UniBtnPressed():
                self._com_client.set_master_action(master_action.UniBtnPressed(action.btn_index))


            # GENERAL BTNS
            case ui_actions.EnableAllMotors():
                self._com_client.set_master_action(master_action.EnableAllMotors())

            case ui_actions.DisableAllMotors():
                self._com_client.set_master_action(master_action.DisableAllMotors())

            case ui_actions.SetZero():
                self._com_client.set_master_action(master_action.SetZero())

            case ui_actions.GoToZero():
                self._com_client.set_master_action(master_action.GoToZero())



            case ui_actions.OnCVCordsSet():
                def map_value(x, in_min, in_max, out_min, out_max):
                    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
                print("on cord set")
                print("action cords", action.boxes)
                mapped_boxes = 0
                for i, box in enumerate(action.boxes):
                    if i < 3:
                        mapped_boxes += 1
                        # print(f"box{i}_x: ", int(box["y"]))
                        x = box["x"]
                        y = box["y"]
                        angle = int(box["angle"]) * -1
                        print("angle: ", angle)

                        paper_width = 230
                        offset_from_pipe = 110
                        xm = paper_width - int(map_value(x, self.offset_x0, self.offset_x1, 0, paper_width)) + offset_from_pipe
                        xm *= -1
                        # print(xm)

                        ym = int(map_value(y, self.offset_y0, self.offset_y1, 0, 210)) - 105
                        # print("ym", ym)

                        self._com_client.add_fpp_variable(f"box{i}_x", xm)
                        self._com_client.add_fpp_variable(f"box{i}_y", ym)
                        self._com_client.add_fpp_variable(f"box{i}_a", angle)

                self._com_client.add_fpp_variable("new_cam_data", mapped_boxes)
                    

            case ui_actions.OnStartRecording():
                self._camera_service.start()

            case ui_actions.OnStopRecording():
                self._camera_service.pause()

            case ui_actions.OnChangeBrightnessThreshold():
                self._detector.threshold = int(float(action.brightness))

            case ui_actions.OnCamOffsetSet():
                self.offset_x0 = action.offsets[0]
                self.offset_x1 = action.offsets[1]
                self.offset_y0 = action.offsets[2]
                self.offset_y1 = action.offsets[3]

            case ui_actions.OnTestAction():
                self._com_client.test_send_v3_packet(action.param)



    def _run_fpp_script(self, file_name: str):

        if file_name.find(".") < 0:
            file_name += ".fpp"
        print("file name: ", file_name)

        lines = self.loader.load(self._context.fpp_dir / file_name)
        cmds = self.parser.parse(lines)


        self._com_client.set_fpp_cmds(cmds)





    # command client
    def _handle_on_slave_action(self, action: slave_action.SlaveAction):
        match(action):
            case slave_action.OnFppScriptStart():
                self._fire_logic_action(logic_actions.OnFppScriptStart(action.size))
            case slave_action.OnFppScriptEnd():
                self._fire_logic_action(logic_actions.OnFppScriptStop())
            case slave_action.OnCurrIndexUpdate():
                self._fire_logic_action(logic_actions.OnFppScriptIndexUpdate(action.curr_index))


    def _handle_on_joint_move(self, index: int, value: float):
            self._com_client.set_master_action(master_action.OnAccAbsJointMove(index, value))
            self.arm_model.joints[index].angle = value
            self.arm_model.graphical_model.trajectory_vertices = []
            self._update_ee_cords()
            self._fire_logic_action(logic_actions.UpdateArmModelCanvas())


    def _handle_on_EE_cord_move(self, index: int, value: float):

        # print()
        # print("current:", self.arm_model.ee_position)
        # print("target:", self.arm_model.target_ee_position)

        target = self.arm_model.target_ee_position
        trajectory = self.arm_model.graphical_model.trajectory_vertices

        if not trajectory:
            # print("reset")
            self.arm_model.target_ee_position = deepcopy(self.arm_model.ee_position)
            x, y, z = self.arm_model.target_ee_position.pos
            trajectory.append(Vertex(x, y, z, "#fc2424", 5))

        # print("index:", index)
        # print("value:", value)
        if index < 3:
            self.arm_model.target_ee_position.pos[index] = value
        else:
            print(index, value)
            self.arm_model.target_ee_position.rot[index - 3] = math.radians(value)

        x, y, z = self.arm_model.target_ee_position.pos
        trajectory[0].x = x
        trajectory[0].y = y
        trajectory[0].z = z


        # print("current:", self.arm_model.ee_position)
        # print("target:", self.arm_model.target_ee_position)

        self._fire_logic_action(logic_actions.UpdateArmModelCanvas())




    # serial state control
    def _handle_on_change_serial_state(self, curr_btn_state: str):
        match(curr_btn_state):
            case "Connect":
                self.on_serial_connect()
            case "Disconnect":
                self.on_serial_disconnect()
            case "Stop":
                self.on_serial_stop_reconnecting()

    def on_serial_connect(self):
        self._ser_client.connect(self._serial_model.port, self._serial_model.baudrate)

    def on_serial_disconnect(self):
        self._ser_client.disconnect()

    def on_serial_stop_reconnecting(self):
        self._ser_client.stop_reconnecting()


    def _handle_new_serial_msg(self, msg: str):
        # print("new msg from vm: ", msg)
        self._new_serial_lines.append(msg)


    def on_send_test_msg(self):
        self._ser_client.send(b"test")

    def get_serial_port_list(self) -> list[str]:
        return self._ser_client.get_port_list()

    def consume_new_serial_lines(self) -> list[str]:

        lines = list(self._new_serial_lines)
        self._new_serial_lines.clear()
        return lines

    
    # callback for serial client
    def on_state_change_callback(self, state: ConnectionState):
        # print("FROM VM state:", state.name)
        self._send_logic_action(logic_actions.SetNewSerialState(state))
    def _handle_send_error_callback(self):
        self._handle_new_serial_msg("- cannot send message while not connected -")
    def _handle_cannot_connect_callback(self, e):
        print(e)
        self._handle_new_serial_msg(str(e))
        # self._new_monitor_msg = True


    def _update_ee_cords(self):
        pos, _ = FK.calculate_FK(self.arm_model.joints)
        rot = (FK.get_pitch_in_4DOF(self.arm_model.joints), 0, 0)
        self.arm_model.ee_position.pos = list(pos)
        self.arm_model.ee_position.rot = list(rot)
        self._fire_logic_action(logic_actions.UpdateEECordValues(
            self.arm_model.ee_position.pos + self.arm_model.ee_position.rot
        ))




    def _send_logic_action(self, action: logic_actions.LogicAction):
        # print("vm sending logical: ", action.__class__.__name__)
        if self._fire_logic_action:
            # print("sended")
            self._fire_logic_action(action)
            
    def set_on_logic_action(self, callback: Callable[[logic_actions.LogicAction], None]):
        self._fire_logic_action = callback


        self._update_ee_cords()


    def get_cam_frame(self):
        frame = self._camera_service.get_frame()
        if frame is not None:
            return self._detector.process(frame)
        return None
    


    





