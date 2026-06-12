from enum import Enum

class InstructionLookup(Enum):
    MOVE_4_TIMED = "MOVE4_T"            # MOVE4_T X0 Y200 Z-200 P90 T30000
    MOVE_4_IND = "MOVE4_I"              # MOVE4_T X0 Y200 Z-200 P90
    MOVE_4_FAST = "MOVE4_F"
    MOVE_45_TIMED = "MOVE44_T"          # MOVE44_T X0 Y200 Z-200 P90 A 30 T6000
    MOVE_33_MANUAL_TIMED = "MOVE33_MT"  # MOVE33_MT X0 Y200 Z-200 A45 B-90 C0 T6000
    MOVE_6_TIMED = "MOVE6_T"            # MOVE6_T X0 Y200 Z-200 P30 A-50 R0 T6000

    CONFIRM = "CONF"                    # CONF
    
    ROTATE = "ROTATE"                   # ROTATE I1 S500
    DELAY = "DELAY"                     # DELAY T2000
    WAIT = "WAIT"                       # WAIT
    HOME = "HOME"                       # HOME
    PWM = "PWM"                         # PWM X50

    EXIT = "EXIT"                       # EXIT

    VAL = "VAL"                         # VAL value
    INCREMENT = "INC"                   # INC value     # value++
    CONDITION = "IF"                    # IF value >= 10
    LABEL = "LABEL"
    GOTO = "GOTO"

    PRINT = "PRINT"                     # PRINT value   |   PRINT "hello world"

    CALCULATE = "CALC"                  # CALC result = value + 10





