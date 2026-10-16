from data.serial.serial_client import SerialClient
from typing import Callable
from domain.model.actions import master_action
from domain.model.actions import slave_action
from domain.model.arm_model import JointHardware
import math
import threading
import time
from collections import deque
from enum import Enum, auto
from domain.motion import IK
import struct
from domain.model import arm_model
from domain.gcode import fpp_commands
from domain.model.packet_model import PacketModel
import re
import operator



class SendItems(Enum):
    JOINT_ANGLE = auto()
    ACC_MOTION = auto()
    PWM_VALUE = auto()

class CommandClient:
    def __init__(self, serial_client: SerialClient):
        self._client = serial_client
        self.hardware_model: tuple[JointHardware] | None = None

        self._client.subscribe(self._handle_new_serial_traffic)

        self._on_slave_action: Callable[[slave_action.SlaveAction], None]

        self._latest = {}

        self._lock = threading.Lock()
        self._running = True
        threading.Thread(target=self._worker, daemon=True).start()

        # real packet communication
        self._instruction_set = []
        self._curr_instr_index = 0
        self._waiting_for_ack = False
        self._waiting_for_done = False
        self._current_packet: PacketModel | None = None
        self._curr_seq_number: int = 0
        self._packet_retry_count = 0
        self._single_instr_count = 0

        self.joints: tuple[arm_model.Joint] | None = None
        self.hardware: tuple[arm_model.JointHardware] | None = None

        #fpp
        self._fpp_labels = {}
        self._fpp_variables = {}
        self._is_fpp_running = False

        self._enable_debug_print = False


    def test_send_v3_packet(self, param):
        print("sending packets")

        start_1 = 0xAA
        start_2 = 0x55

        header = 0xCB
        staff = 0x01

        data = [
            10,
            20,
            30,
            40,
            50,
            60,
            70
        ]

        msg_index = param
        if msg_index == None:
            msg_index = 0

        packet = struct.pack(
            "<BBBB7iB",
            start_1,
            start_2,
            header,
            staff,
            *data,
            msg_index
        )

        control_sum = (sum(packet) - start_1 - start_2) & 0xFF

        packet = packet + struct.pack("B", control_sum)

        print(packet)
        print(len(packet))

        self._client.send(packet)



    def set_master_action(self, action: master_action.MasterAction):
        match(action):

            case master_action.SetZero():
                print("setting zero")
                
                packet = self.build_packet_v3(ord("z"), ord("a"), (0,), 1)
                packet_blank = self.build_packet_v3(0, 0, (0,), 2)
            
                self._single_instr_count = 2
                self.set_fpp_cmds((PacketModel(packet, seq_number=1), PacketModel(packet_blank, seq_number=2)))

            case master_action.GoToZero():
                print("goto zero")
                
                packet = self.build_packet_v3(ord("a"), ord("a"), (0,), 1)
                packet_blank = self.build_packet_v3(0, 0, (0,), 2)
                
                self._single_instr_count = 2
                self.set_fpp_cmds((PacketModel(packet, seq_number=1), PacketModel(packet_blank, seq_number=2)))

            case master_action.OnAccAbsJointMove():
                self._handle_acc_joint_move(action.joint_index, action.value)

            # case master_action.OnPWMMove():
            #     self._handle_pwm_move(action.index, action.value)

            case master_action.OnSetAccMovement():
                self._handle_toggle_acc_movement(action.state)

            case master_action.On4DoFMove():
                print("\n\nhandle 4dof")

                data: bytearray = self._handle_4DoF_Move(action.x, action.y, action.z, action.pitch, action.time)
                packet = PacketModel(data, seq_number=1)
                packet_blank = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), 2)
                # self._instruction_set.append(PacketModel(packet))
                # self._instruction_set.append(PacketModel(packet_blank))
            
                self.set_fpp_cmds((packet, PacketModel(packet_blank, seq_number=2)))


            case master_action.StopFppRunning():
                self._is_fpp_running = False
                self._on_slave_action(slave_action.OnFppScriptEnd())

            case master_action.UniBtnPressed():
                btn = f"btn{action.btn_index}"
                # print(btn, "pressed from fpp")
                self._fpp_variables[btn] = 1

            case master_action.EnableAllMotors():

                print("\nenable all motors")

                packet = self.build_packet_v3(ord("e"), ord("a"), (1,), 1)
                packet_blank = self.build_packet_v3(0, 0, (0,), 2)
            
                self._single_instr_count = 2
                self.set_fpp_cmds((PacketModel(packet, seq_number=1), PacketModel(packet_blank, seq_number=2)))

            case master_action.DisableAllMotors():

                print("\disable all motors")

                packet = self.build_packet_v3(ord("e"), ord("a"), (0,), 1)
                packet_blank = self.build_packet_v3(0, 0, (0,), 2)

                self._single_instr_count = 2
                self.set_fpp_cmds((PacketModel(packet, seq_number=1), PacketModel(packet_blank, seq_number=2)))

    def build_packet_v3(self, header: int, staff: int, data: list[int], seq_index: int):

        data = tuple(data) + (0,) * (7 - len(data))
        data = data[:7]

        start_1 = 0xAA
        start_2 = 0x55

        # print("building v3: ", seq_index)

        packet = struct.pack(
            "<BBBB7iB",
            start_1,
            start_2,
            header,
            staff,
            *data,
            seq_index
        )

        control_sum = (sum(packet) - start_1 - start_2) & 0xFF

        packet = packet + struct.pack("B", control_sum)

        # print(packet)
        # print(len(packet))
        return packet

    def add_fpp_variable(self, name: str, value: int):
        self._fpp_variables[name] = value
        print("adding fpp var: ", self._fpp_variables)

        
    # loads all cmds into this class
    def set_fpp_cmds(self, cmds: list[fpp_commands.FppCommand]):
        self._waiting_for_ack = False
        self._waiting_for_done = False
        self._packet_retry_count = 0
        self._instruction_set = []
        self._curr_instr_index = 0
        self._current_packet = None

        self._fpp_labels = {}
        self._fpp_variables = {
            "btn0": 0,
            "btn1": 0,
            "btn2": 0,
            "new_cam_data": 0
        }

        seq = 0

        for cmd in cmds:
            seq = (seq + 1) & 0xff

            match(cmd):
                case fpp_commands.MoveJoint():  # deprecated
                    pass
                    # print("adding move joint")
                    # packet = f"a {cmd.index} :{cmd.pos};\n"
                    # packet = packet.encode("ascii", errors="ignore")
                    # self._send_packet(packet)

                # case fpp_commands.WaitTillDone():
                #     # print("adding wait")
                #     packet = self.build_packet_v3(ord("W"), 0, (0,), seq)
                #     seq = (seq + 1) & 0xff
                #     confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                #     self._instruction_set.append(PacketModel(packet))
                #     self._instruction_set.append(PacketModel(confirm_packet, wait_for_done=True))

                # case fpp_commands.DelayMs():
                #     delay = self._return_value_or_variable(cmd.time)
                #     packet = self.build_packet_v3(ord("D"), 0, (delay,), seq)
                #     seq = (seq + 1) & 0xff
                #     confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                #     self._instruction_set.append(PacketModel(packet))
                #     self._instruction_set.append(PacketModel(confirm_packet, wait_for_done=True))

                # case fpp_commands.GoToPos4DOFTimed():
                #     x = self._return_value_or_variable(cmd.x)
                #     y = self._return_value_or_variable(cmd.y)
                #     z = self._return_value_or_variable(cmd.z)
                #     print(cmd.pitch)
                #     pitch = self._return_value_or_variable(cmd.pitch)
                #     time = self._return_value_or_variable(cmd.time)

                #     pitch = math.radians(pitch)

                #     data: bytearray = self._handle_4DoF_Move(x, y, z, pitch, time, seq=seq)
                #     packet = PacketModel(data, seq_number=seq)
                #     self._instruction_set.append(packet)

                #     seq = (seq + 1) & 0xff
                #     if (cmd.wait):
                #         confirm_packet = self.build_packet_v3(ord("W"), 0, (0,), seq)
                #     else:
                #         confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                #     self._instruction_set.append(PacketModel(confirm_packet, seq_number=seq))

                # case fpp_commands.GoToPos4DOFIndependent():
                #     data: bytearray = self._handle_4DoF_Move(cmd.x, cmd.y, cmd.z, cmd.pitch, -1, seq=seq)
                #     packet = PacketModel(data, seq_number=seq)
                #     seq = (seq + 1) & 0xff
                #     confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                #     self._instruction_set.append(packet)
                #     self._instruction_set.append(PacketModel(confirm_packet, seq_number=seq))

                # case fpp_commands.GoToPos3DOF3ManualTimed():
                #     data: bytearray = self._handle_3DOF_3manual_move(cmd.x, cmd.y, cmd.z, cmd.a, cmd.b, cmd.c, cmd.time)
                #     packet = PacketModel(data, seq_number=seq)
                #     seq = (seq + 1) & 0xff
                #     confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                #     self._instruction_set.append(packet)
                #     self._instruction_set.append(PacketModel(confirm_packet, seq_number=seq))

                    

                # case fpp_commands.GoHome():
                #     self._send_packet(b"a a :0;\n")

                # case fpp_commands.MovePWM():
                #     packet = self.build_packet_v3(ord("p"), ord("y"), (cmd.value,), seq)
                #     seq = (seq + 1) & 0xff
                #     confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                #     self._instruction_set.append(PacketModel(packet))
                #     self._instruction_set.append(PacketModel(confirm_packet))


                case _:
                    self._instruction_set.append(cmd)

        print("all instructions: ", self._instruction_set)
        # self._try_send_next_packet()

        # loads all labels
        for i, instr in enumerate(self._instruction_set):
            if isinstance(instr, fpp_commands.Label):
                self._fpp_labels[instr.label_name] = i

        self._is_fpp_running = True
        self._on_slave_action(slave_action.OnFppScriptStart(len(self._instruction_set)))
        self._try_execute_next_instr()
        



    def _handle_new_serial_traffic(self, msg: str):
        # print("from command client:" , msg)
        # ack
        if msg.startswith(b"\xaa\x55\xf0"): 
            print("v3 ack")
            print("wait for ack: ", self._waiting_for_ack)
            print("wait for done: ", self._waiting_for_done)
            self._waiting_for_ack = False
            self._current_packet = None
            if not self._waiting_for_ack and not self._waiting_for_done:
                self._curr_instr_index += 1
                self._try_execute_next_instr()

        # nack
        if msg.startswith(b"\xaa\x55\x0f"):
            print("v3 nack")
            self._resend_current()

        # done
        if msg.startswith(b"\xaa\x55\xff"):
            print("done")
            print("wait for ack: ", self._waiting_for_ack)
            print("wait for done: ", self._waiting_for_done)
            self._waiting_for_done = False
            self._current_packet = None
            if not self._waiting_for_ack and not self._waiting_for_done:
                self._curr_instr_index += 1
                self._try_execute_next_instr()
            # self._try_send_next_packet()

        

        # if msg.startswith(b"ACK"):
        #     # print("ack")
        #     self._waiting_for_ack = False
        #     self._current_packet = None
        #     if not self._waiting_for_ack and not self._waiting_for_done:
        #         self._curr_instr_index += 1
        #         self._try_execute_next_instr()
        #     # self._try_send_next_packet()

        # if msg.find(b"DONE") > -1:
        #     # print("done")
        #     self._waiting_for_done = False
        #     self._current_packet = None
        #     if not self._waiting_for_ack and not self._waiting_for_done:
        #         self._curr_instr_index += 1
        #         self._try_execute_next_instr()
        #     # self._try_send_next_packet()

        # elif msg.find(b"NACK") > -1:
        #     print("nack")
        #     self._resend_current()

    def _send_packet(self, packet: bytes, wait_for_ack: bool=True, wait_for_done: bool=False, send_now=False):
        self._instruction_set.append(PacketModel(packet, wait_for_ack, wait_for_done))
        if send_now:
            self._try_send_next_packet()

    
    def _try_execute_next_instr(self):
        if self._enable_debug_print:
            print("start executing next instruction")
        if not self._is_fpp_running:
            return
        
        if self._enable_debug_print:
            print("executing")

        if self._curr_instr_index >= len(self._instruction_set):
            print("all cmds are done")
            return

        while isinstance(self._instruction_set[self._curr_instr_index], fpp_commands.FppCommand):
            if not self._is_fpp_running:
                return

            instr = self._instruction_set[self._curr_instr_index]

            if self._enable_debug_print:
                print("\nfpp cmd: ", instr)

            time.sleep(0.01)

            if self._enable_debug_print:
                print("match start")
            match instr:
                
                # PHYSICAL COMMANDS

                case fpp_commands.GoToPos4DOFTimed():
                    print("goind to 4")
                    x = self._return_value_or_variable(instr.x)
                    y = self._return_value_or_variable(instr.y)
                    z = self._return_value_or_variable(instr.z)
                    pitch = self._return_value_or_variable(instr.pitch)
                    time_ms = self._return_value_or_variable(instr.time)

                    pitch = math.radians(pitch)
                    seq = self._get_seq_number()
                    # print("seq", seq)
                    data: bytearray = self._handle_4DoF_Move(x, y, z, pitch, time_ms, seq)
                    packet = PacketModel(data, seq_number=seq)
                    self._current_packet = packet
                    self._try_send_next_packet()
                    break

                case fpp_commands.GoToPos4DOFIndependent():
                    x = self._return_value_or_variable(instr.x)
                    y = self._return_value_or_variable(instr.y)
                    z = self._return_value_or_variable(instr.z)
                    pitch = self._return_value_or_variable(instr.pitch)
                    pitch = math.radians(pitch)
                    
                    seq = self._get_seq_number()
                    data: bytearray = self._handle_4DoF_Move(x, y, z, pitch, -1, seq=seq)
                    packet = PacketModel(data, seq_number=seq)
                    self._current_packet = packet
                    self._try_send_next_packet()
                    break

                case fpp_commands.GoTo4dot5DOFTimed():
                    x = self._return_value_or_variable(instr.x)
                    y = self._return_value_or_variable(instr.y)
                    z = self._return_value_or_variable(instr.z)
                    print("pitch: ", instr.pitch)
                    p = self._return_value_or_variable(instr.pitch)
                    a = self._return_value_or_variable(instr.alpha)
                    print("case: ", instr.time)
                    time_ms = self._return_value_or_variable(instr.time)
                    pitch = math.radians(p)
                    alpha = math.radians(a)

                    print("going 4.5 dof move")

                    seq = self._get_seq_number()
                    data: bytearray = self._handle_4dot5DOF_move(x, y, z, pitch, alpha, time_ms)
                    packet = PacketModel(data, seq_number=seq)
                    self._current_packet = packet
                    self._try_send_next_packet()
                    break

                    

                case fpp_commands.GoToPos3DOF3ManualTimed():
                    x = self._return_value_or_variable(instr.x)
                    y = self._return_value_or_variable(instr.y)
                    z = self._return_value_or_variable(instr.z)
                    a = self._return_value_or_variable(instr.a)
                    b = self._return_value_or_variable(instr.b)
                    c = self._return_value_or_variable(instr.c)
                    time_ms = self._return_value_or_variable(instr.time)
                    seq = self._get_seq_number()
                    data: bytearray = self._handle_3DOF_3manual_move(x, y, z, a, b, c, time_ms, seq=seq)
                    packet = PacketModel(data, seq_number=seq)
                    self._current_packet = packet
                    self._try_send_next_packet()
                    break


                case fpp_commands.Confirm():
                    print("confirming", instr.wait_for_done)
                    seq = self._get_seq_number()
                    # print("seq", seq)
                    confirm_packet = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), seq)
                    packet: PacketModel = PacketModel(confirm_packet, seq_number=seq, wait_for_done=instr.wait_for_done)
                    self._current_packet = packet
                    if instr.wait_for_done:
                        print("waiting fro done")
                    self._try_send_next_packet()
                    break
                
                
                case fpp_commands.DelayMs():
                    print("executing delay")
                    delay = self._return_value_or_variable(instr.time)
                    seq = self._get_seq_number()
                    # print("seq", seq)
                    packet = self.build_packet_v3(ord("D"), 0, (int(delay),), seq)
                    self._current_packet = PacketModel(packet, seq_number=seq)
                    self._try_send_next_packet()
                    break

                case fpp_commands.WaitTillDone():
                    print("executing wait")
                    seq = self._get_seq_number()
                    # print("seq", seq)
                    packet = self.build_packet_v3(ord("W"), 0, (0,), seq)
                    self._current_packet = PacketModel(packet, seq_number=seq)
                    self._try_send_next_packet()
                    break

                case fpp_commands.MovePWM():
                    print(instr.value)
                    value = self._return_value_or_variable(instr.value)

                    seq = self._get_seq_number()
                    packet = self.build_packet_v3(ord("p"), ord("y"), (int(value),), seq)
                    self._current_packet = PacketModel(packet, seq_number=seq)
                    self._try_send_next_packet()
                    break

                # FLOW COMMANDS

                case fpp_commands.Value():
                    value = self._return_value_or_variable(instr.value)
                    if self._enable_debug_print:
                        print("value with name:", instr.name, "with value:", instr.value)
                    self._fpp_variables[instr.name] = value
                case fpp_commands.Label():
                    pass # labels are already loaded
                    
                    # print("label with name:", instr.label_name, "value of the index is:", self._curr_instr_index)
                    # self._fpp_labels[instr.label_name] = self._curr_instr_index
                case fpp_commands.GoTo():
                    if self._enable_debug_print:
                        print("goto to label with name:", instr.label_name)
                    self._curr_instr_index = self._fpp_labels[instr.label_name]
                    if self._enable_debug_print:
                        print("going to index:", self._curr_instr_index)
                case fpp_commands.Increment():
                    self._fpp_variables[instr.variable_name] += 1; 
                    if self._enable_debug_print:
                        print("incremented var:", instr.variable_name, "to value:", self._fpp_variables[instr.variable_name])
                case fpp_commands.Condition():
                    result = self._evaluate_if(instr.expression)
                    if self._enable_debug_print:
                        print("if result:", result, "  btn0:", self._fpp_variables["btn0"])
                    if result:
                        self._curr_instr_index += 1 # skips the instruction immediately after if
                case fpp_commands.Print():
                    value = instr.value
                    if value.find("\"") > -1:
                        print("print str:", instr.value)
                    else:
                        print("print val:", self._fpp_variables[value])

                case fpp_commands.Calculate():
                    res = self._execute_calculate(instr)
                    self._fpp_variables[instr.result] = res



            self._curr_instr_index += 1
            self._on_slave_action(slave_action.OnCurrIndexUpdate(self._curr_instr_index))
            if self._curr_instr_index >= len(self._instruction_set):
                print("\nALL CMDS ARE DONE\n")
                self._is_fpp_running = False
                self._on_slave_action(slave_action.OnFppScriptEnd())
                return

        if self._enable_debug_print:
            print("end match")
        if self._single_instr_count > 0:
            self._single_instr_count -= 1
            print("\ninstr is single packet")
            packet: PacketModel = self._instruction_set[self._curr_instr_index]
            print("packet:", packet)
            self._current_packet = packet
            self._try_send_next_packet()


    def _try_send_next_packet(self):
        # print("trying to send packets")
        if self._waiting_for_ack:
            # print("return ack")
            return
        if self._waiting_for_done:
            # print("return not done")
            return
        if self._curr_instr_index > len(self._instruction_set):
            print("return none packets")
            print("curr index", self._curr_instr_index)
            print("len of set", len(self._instruction_set))
            print(self._curr_instr_index)
            self._waiting_for_ack = False
            return
        
        # try:
        #     self._current_packet = self._instruction_set[self._curr_instr_index]
        # except:
        #     print("error")
        # print("sending packet")

        self._curr_seq_number = self._current_packet.seq_number
        if self._current_packet.wait_for_ack:
            self._waiting_for_ack = True
        if self._current_packet.wait_for_done:
            self._waiting_for_done = True

        # print("sending packet: ", " ".join(f"0x{b:02X}" for b in self._current_packet.packet))
        print("sending packet:", self._current_packet)
        self._client.send(self._current_packet.packet)

        self._packet_retry_count = 0



    def _resend_current(self):
        print("resending packet")
        if self._packet_retry_count >= 3:
            self._waiting_for_ack = False
            self._current_packet = None
            print("packer retry over limit")
            return
        
        self._packet_retry_count += 1
        print("resending: ", " ".join(f"0x{b:02X}" for b in self._current_packet.packet))
        print("retry count", self._packet_retry_count)
        self._client.send(self._current_packet.packet)

    def _execute_calculate(self, instr: fpp_commands.Calculate):
    
        # print("calculating: ", instr.result, instr.first_value, instr.operator, instr.second_value)

        first = instr.first_value
        if (self._is_variable(first)):
            first = self._fpp_variables[first]
        else:
            first = int(first)
        
        second = instr.second_value
        if (self._is_variable(second)):
            second = self._fpp_variables[second]
        else:
            second = int(second)

        match(instr.operator):
            case "+": return first + second
            case "-": return first - second
            case "*": return first * second
            case "/": return first / second



    def _is_variable(self, value: str) -> bool:
        return not all(c.isdigit() or c in '-.' for c in value)
    
    def _return_value_or_variable(self, value: str):
        value = str(value)
        if value.startswith("_") or value.startswith("="):
            value = value[1:]
        if self._is_variable(value):
            # print(self._fpp_variables)
            return self._fpp_variables[value]
        return float(value)
    
    def _get_seq_number(self):
        self._curr_seq_number = (self._curr_seq_number + 1) & 0xff
        return self._curr_seq_number

    def _evaluate_if(self, expr: str) -> bool:
        ops = {
            ">": operator.gt,
            "<": operator.lt,
            "==": operator.eq,
            "!=": operator.ne,
            ">=": operator.ge,
            "<=": operator.le,
        }
        pattern = r"(\w+)\s*(>=|<=|==|!=|>|<)\s*(\w+)"
        match = re.fullmatch(pattern, expr.strip())

        if not match:
            # TODO: raise compiler exception
            pass

        left, op, right = match.groups()

        if left in self._fpp_variables:
            left_value = self._fpp_variables[left]
        else:
            try:
                left_value = int(left)
            except: 
                # raise wrong value compiler exception
                pass

        
        if right in self._fpp_variables:
            right_value = self._fpp_variables[right]
        else:
            try:
                right_value = int(right)
            except: 
                # raise wrong value compiler exception
                pass

        return ops[op](left_value, right_value)

    def _handle_4dot5DOF_move(self, x: float, y: float, z: float, pitch: float, alpha: float, time_ms: float, seq: int=1):
        print("4.5 dof move")
        
        a, b, c, d = IK.calculate_4DoF_IK([x, y, z], pitch, self.joints)
        alpha = a + alpha
        print("alpha: ", alpha)
        steps = [a, b, c, 0, d, alpha]
        converted_steps = []
        for i, x in enumerate(steps):
            converted_steps.append(
                int((x / (2 * math.pi)) * (self.hardware[i].steps_per_revolution * self.hardware[i].gear_ratio))
            )
            # print(converted_steps[i])
        steps = converted_steps


        if time_ms > 0:
            packet_data = self.build_packet_v3(ord("T"), 0, (steps[0], steps[1], steps[2], steps[3], steps[4], steps[5], int(time_ms)), seq)
        else:
            packet_data = self.build_packet_v3(ord("I"), 0, (steps[0], steps[1], steps[2], steps[3], steps[4], steps[5], 0), seq)


        return packet_data


    def _handle_3DOF_3manual_move(self, x: float, y: float, z: float, a: float, b: float, c: float, time_ms: float, seq: int=1):
        print("33 dof")

        x, y, z = IK._calculate_3Dof_IK([x, y, z], self.joints)

        a = math.radians(a)
        b = math.radians(b)
        c = math.radians(c)

        print(a, b, c)

        steps = [x, y, z, a, b, c]
        converted_steps = []
        for i, x in enumerate(steps):
            converted_steps.append(
                int((x / (2 * math.pi)) * (self.hardware[i].steps_per_revolution * self.hardware[i].gear_ratio))
            )
        steps = converted_steps

        
        if time_ms > 0:
            packet_data = self.build_packet_v3(ord("T"), 0, (steps[0], steps[1], steps[2], steps[3], steps[4], steps[5], int(time_ms)), seq)
        else:
            packet_data = self.build_packet_v3(ord("I"), 0, (steps[0], steps[1], steps[2], steps[3], steps[4], steps[5], 0), seq)

        return packet_data

    def _handle_4DoF_Move(self, x: float, y: float, z: float, pitch: float, time_ms: float, seq: int):
        print("4dof")

        
        a, b, c, d = IK.calculate_4DoF_IK([x, y, z], pitch, self.joints)
        steps = [a, b, c, 0, d, 0]
        converted_steps = []
        for i, x in enumerate(steps):
            converted_steps.append(
                int((x / (2 * math.pi)) * (self.hardware[i].steps_per_revolution * self.hardware[i].gear_ratio))
            )
            # print(converted_steps[i])
        steps = converted_steps

        # self._curr_seq_number = 0

        if time_ms > 0:
            packet_data = self.build_packet_v3(ord("T"), 0, (steps[0], steps[1], steps[2], steps[3], steps[4], steps[5], int(time_ms)), seq)
        else:
            packet_data = self.build_packet_v3(ord("I"), 0, (steps[0], steps[1], steps[2], steps[3], steps[4], steps[5], 0), seq)

        # model_data = PacketModel(packet_data)

        # packet_blank = self.build_packet_v3(0, 0, (0, 0, 0, 0, 0, 0, 0), 2)
        # model_blank = PacketModel(packet_blank, seq_number=2)

        # self.set_gcode_cmds((model_data, model_blank))

        return packet_data

        # packet = "T"
        # for step in steps:
        #     packet += f" :{step}"
        # packet += f" :{time};\n"

        # print("sending:", packet)

        # self._send_packet(packet.encode("ascii", errors="ignore"))

        # self._instruction_set.clear()
        # self._instruction_set.append(PacketModel())
        # self._curr_instr_index = 0
        # self._try_execute_next_instr()


    def _send_active_joint_byte(self, active_joints: int):
        
        header = 0xff
        new_line = 0x0a

        packet = bytearray()
        packet.append(header)
        packet.append(active_joints)
        
        for _ in range(28): # 28 to send 27
            packet.append(0x00)

        control_sum = sum(packet) & 0xff
        print("my sum joint", control_sum)
        packet.append(control_sum)
        packet.append(new_line)

        self._instruction_set.append(PacketModel(packet))
            
    def _handle_pwm_move(self, index: int, value: float):
        channel = "y" if index else "x"
        msg = f"p {channel} :{int(value)};\n"
        # print(msg)
        self._add_to_latest(SendItems.PWM_VALUE, msg)
        # self._client.send(msg.encode("ascii", errors="ignore"))

    def _handle_acc_joint_move(self, index: int, value: float):
        j = self.hardware_model[index]
        steps = int((j.steps_per_revolution * j.gear_ratio) * (value / (2 * math.pi)))
        # msg = f"w {index + 1} :{steps};\n"
        # print(msg)
        # self._client.send(msg.encode("ascii", errors="ignore"))
        # self._add_to_latest(SendItems.JOINT_ANGLE, msg)

        print("manual index:", index, "  value:", value)

        data = self.build_packet_v3(ord("w"), index, (steps,), 1)
        packet = PacketModel(data, seq_number=1)
        blank_packet = PacketModel(self.build_packet_v3(0, 0, (0,), 2), seq_number=2)

        self._single_instr_count = 2
        self.set_fpp_cmds((packet, blank_packet))



    def _handle_toggle_acc_movement(self, state):
        state = 1 if state else 0

        print("acc set to all:", state)

        data = self.build_packet_v3(ord("f"), ord("a"), (state,), 1)
        packet = PacketModel(data, seq_number=1)
        blank_packet = PacketModel(self.build_packet_v3(0, 0, (0,), 2), seq_number=2)

        self._single_instr_count = 2
        self.set_fpp_cmds((packet, blank_packet))



    def _add_to_latest(self, key, value):
        with self._lock:
            self._latest[key] = value


    def _worker(self):
        while self._running:
            time.sleep(0.05)
            with self._lock:
                data = self._latest
                self._latest = {}
            
            for _, value in data.items():
                print("value in th", value)
                self._client.send(value.encode("ascii", errors="ignore"))



    def subscribe_slave_action(self, callback: Callable[[slave_action.SlaveAction], None]):
        self._on_slave_action = callback




