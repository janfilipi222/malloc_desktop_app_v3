from dataclasses import dataclass
from data.serial.connection_state import ConnectionState

class LogicAction:
    pass


# serial actions
@dataclass(frozen=True)
class SetNewSerialState(LogicAction):
    state: ConnectionState

@dataclass(frozen=True)
class SetNewPortList(LogicAction):
    ports: list[str]


@dataclass(frozen=True)
class UpdateArmModelCanvas(LogicAction):
    pass


@dataclass(frozen=True)
class UpdateEECordValues(LogicAction):
    values: list[float] # 0, 1, 2 = positions | 3, 4, 5 = rotations


# fpp actions
@dataclass(frozen=True)
class SetNewPffScriptList(LogicAction):
    scripts: list[str]

@dataclass(frozen=True)
class OnFppScriptStart(LogicAction):
    size: int

@dataclass(frozen=True)
class OnFppScriptStop(LogicAction):
    pass

@dataclass(frozen=True)
class OnFppScriptIndexUpdate(LogicAction):
    curr_index: int

