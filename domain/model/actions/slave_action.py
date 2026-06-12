from dataclasses import dataclass


class SlaveAction:
    pass





#fpp actions
@dataclass(frozen=True)
class OnFppScriptStart(SlaveAction):
    size: int

@dataclass(frozen=True)
class OnFppScriptEnd(SlaveAction):
    pass

@dataclass(frozen=True)
class OnCurrIndexUpdate(SlaveAction):
    curr_index: int



