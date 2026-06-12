

#PWM Y50
#CONF
#EXIT

VAL dif = -10
VAL int value = 0

LABEL start

PWM Y=value


CALC value = value - dif

DELAY T500
CONF W

GOTO start


EXIT


VAL z: int= -170
VAL time: int= 3000
LABEL start
MOVE4_T X0 Y200 Z=z P90 T=time
WAIT
CONF W

CALC z = z - 10
VAL time: int= 1000

PRINT z
GOTO start



DELAY T2000
CONF W

EXIT


VAL y: int= 200
MOVE4_T X0 Y=y Z-200 P90 T5000
#WAIT

EXIT




VAL i: int= 8
VAL res: int= 0


CALC res = i + i
INC res


PRINT res