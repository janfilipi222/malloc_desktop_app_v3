from dataclasses import dataclass


class FppCommand:
    pass


# PHYSICAL COMMANDS

@dataclass(frozen=True)
class WaitTillDone(FppCommand):      # waits till all joints are not moving
    pass

@dataclass(frozen=True)
class DelayMs(FppCommand):           # does nothing for the time
    time: str # str bcs it can be variable name

@dataclass(frozen=True)
class MoveJoint(FppCommand):         # moves specific joint to the abs pos
    index: int # 0 to 5
    pos: int # abs position in steps


@dataclass(frozen=True)
class GoToPos4DOFTimed(FppCommand):  # moves the ee to the pos in 4DOF system
    x: str  # str bcs they can contain variable reference
    y: str
    z: str
    pitch: str
    time: str # time in ms
    wait: bool

@dataclass(frozen=True)
class GoToPos4DOFIndependent(FppCommand):
    x: str
    y: str
    z: str
    pitch: str
    wait: bool

@dataclass(frozen=True)
class GoTo4dot5DOFTimed(FppCommand):
    x: str
    y: str
    z: str
    pitch: str
    alpha: str
    time: str
    wait: bool

@dataclass(frozen=True)
class GoToPos3DOF3ManualTimed(FppCommand):
    x: float
    y: float
    z: float
    a: float    # angle of the 4th joint in radian
    b: float    # angle of the 5th joint in radian
    c: float    # angle of the 6th joint in radian
    time: int
    wait: bool

@dataclass(frozen=True)
class GoToPos6DOFTimed(FppCommand):
    x: float
    y: float
    z: float
    p: float    # pitch angle in radian
    y: float    # yaw angle in radian
    r: float    # roll angle in radian    
    time: int
    wait: bool

@dataclass(frozen=True) 
class GoHome(FppCommand):            # moves all joints to 0 abs pos
    pass

@dataclass(frozen=True)
class MovePWM(FppCommand):           # sets the pwm value to the channel
    channel: str # x or y
    value: str

@dataclass(frozen=True)
class Confirm(FppCommand):          # sends blank packet to execute previous packet
    wait_for_done: bool = False


# FLOW COMMANDS

@dataclass(frozen=True)
class Value(FppCommand):
    name: str
    type: str
    value: str # can be name of the variable

@dataclass(frozen=True)
class GoTo(FppCommand):
    label_name: str

@dataclass(frozen=True)
class Label(FppCommand):
    label_name: str

@dataclass(frozen=True)
class Increment(FppCommand):
    variable_name: str

@dataclass(frozen=True)
class Condition(FppCommand):
    expression: str

@dataclass(frozen=True)
class Print(FppCommand):
    value: str

@dataclass(frozen=True)
class Calculate(FppCommand):
    result: str
    first_value: str
    second_value: str 
    operator: str
