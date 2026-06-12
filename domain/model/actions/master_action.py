from dataclasses import dataclass


class MasterAction:
    pass


@dataclass(frozen=True)
class OnAccAbsJointMove(MasterAction):
    joint_index: int # 0, 1, ..., 5
    value: float     # in rad


@dataclass(frozen=True)
class OnPWMMove(MasterAction):
    index: int # x or y
    value: float # value in ms


@dataclass(frozen=True)
class OnSetAccMovement(MasterAction):
    state: bool


@dataclass(frozen=True)
class On4DoFMove(MasterAction):
    x: float # in mm
    y: float # in mm
    z: float # in mm
    pitch: float # in rad - zero = horizontal
    time: float # time in ms



# fpp
@dataclass(frozen=True)
class StopFppRunning(MasterAction):
    pass

@dataclass(frozen=True)
class UniBtnPressed(MasterAction):
    btn_index: int

@dataclass(frozen=True)
class EnableAllMotors(MasterAction):
    pass

@dataclass(frozen=True)
class DisableAllMotors(MasterAction):
    pass

@dataclass(frozen=True)
class SetZero(MasterAction):
    pass

@dataclass(frozen=True)
class GoToZero(MasterAction):
    pass









