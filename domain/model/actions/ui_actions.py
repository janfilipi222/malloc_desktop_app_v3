from dataclasses import dataclass

class UIAction:
    pass


# serial monitor actions
@dataclass(frozen=True)
class OnPortSelect(UIAction):
    port: str

@dataclass(frozen=True)
class OnPortsUpdate(UIAction):
    pass

@dataclass(frozen=True)
class OnSerialSend(UIAction):
    msg: str

@dataclass(frozen=True)
class OnChangeSerialState(UIAction):
    btn_text: str

@dataclass(frozen=True)
class OnSerialClear(UIAction):
    pass




# manual control actions
@dataclass(frozen=True)
class OnJointMove(UIAction):
    index: int # 0 - 5
    value: float # rad

@dataclass(frozen=True)
class OnToggleAccMove(UIAction):
    state: bool

@dataclass(frozen=True)
class OnEECordMove(UIAction):
    index: int # 0 - 5
    value: float # cord in mm  OR  rot in rad

@dataclass(frozen=True)
class OnGoCordButton(UIAction):
    time: float

@dataclass(frozen=True)
class OnPWMMove(UIAction):
    index: int # index of pwm channel ("x" or "y")
    value: float # value in ms



# fpp actions
@dataclass(frozen=True)
class UpdateFppScriptList(UIAction):
    pass

@dataclass(frozen=True)
class RunFppScript(UIAction):
    file_name: str

@dataclass(frozen=True)
class StopFppScript(UIAction):
    pass

@dataclass(frozen=True)
class UniBtnPressed(UIAction):
    btn_index: int
    
@dataclass(frozen=True)
class EnableAllMotors(UIAction):
    pass

@dataclass(frozen=True)
class DisableAllMotors(UIAction):
    pass

@dataclass(frozen=True)
class SetZero(UIAction):
    pass

@dataclass(frozen=True)
class GoToZero(UIAction):
    pass




@dataclass(frozen=True)
class OnStartRecording(UIAction):
    pass

@dataclass(frozen=True)
class OnStopRecording(UIAction):
    pass

@dataclass(frozen=True)
class OnCVCordsSet(UIAction):
    boxes: list

@dataclass(frozen=True)
class OnChangeBrightnessThreshold(UIAction):
    brightness: int

@dataclass(frozen=True)
class OnCamOffsetSet(UIAction):
    offsets: list


@dataclass(frozen=True)
class OnTestAction(UIAction):
    param: int



