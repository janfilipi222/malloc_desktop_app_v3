
PWM Y97

LABEL loop


    IF (btn0 == 1)
        GOTO if0
        VAL btn0 = 0

        PRINT "btn 0 pressed"

        GOTO left

    LABEL if0

    IF (btn1 == 1)
        GOTO if1
        VAL btn1 = 0

        PRINT "btn 1 pressed"

        GOTO right

    LABEL if1

    IF (btn2 == 1)
        GOTO if2
        VAL btn2 = 0

        PRINT "btn 2 pressed"

        GOTO home


    LABEL if2


GOTO loop





### building the left pyramid
LABEL left

    # to left
    MOVE4_T X-200 Y200 Z80 P90 T500
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y120 Z80 P90 T800
    WAIT
    CONF W

    # grip
    PWM Y87
    #DELAY T150
    #CONF W
    CONF

    # up
    MOVE4_T X-200 Y200 Z80 P90 T800
    WAIT
    CONF W

    # right
    MOVE4_T X-200 Y200 Z-80 P90 T500
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y100 Z-80 P90 T800
    WAIT
    CONF W

    # release
    PWM Y110
    #DELAY T150
    #CONF W
    CONF
    
    # up
    MOVE4_T X-200 Y200 Z-80 P90 T800
    WAIT
    CONF W



    
    # to left
    MOVE4_T X-200 Y200 Z80 P90 T500
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y100 Z80 P90 T800
    WAIT
    CONF W

    # grip
    PWM Y87
    #DELAY T150
    #CONF W
    CONF

    # up
    MOVE4_T X-200 Y200 Z80 P90 T800
    WAIT
    CONF W

    # right
    MOVE4_T X-200 Y200 Z-80 P90 T500
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y120 Z-80 P90 T800
    WAIT
    CONF W

    # release
    PWM Y110
    #DELAY T150
    #CONF W
    CONF
    
    # up
    MOVE4_T X-200 Y200 Z-80 P90 T800
    WAIT
    CONF W

    GOTO loop




### building the right pyramid
LABEL right

    # to right
    MOVE4_T X-200 Y200 Z-80 P90 T1000
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y120 Z-80 P90 T1000
    WAIT
    CONF W

    # grip
    PWM Y87
    DELAY T300
    CONF W

    # up
    MOVE4_T X-200 Y200 Z-80 P90 T1000
    WAIT
    CONF W

    # to left
    MOVE4_T X-200 Y200 Z80 P90 T1000
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y100 Z80 P90 T1000
    WAIT
    CONF W

    # release
    PWM Y110
    DELAY T300
    CONF W
    
    # up
    MOVE4_T X-200 Y200 Z80 P90 T1000
    WAIT
    CONF W



    # right
    MOVE4_T X-200 Y200 Z-80 P90 T1000
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y100 Z-80 P90 T1000
    WAIT
    CONF W

    # grip
    PWM Y87
    DELAY T300
    CONF W

    # up
    MOVE4_T X-200 Y200 Z-80 P90 T1000
    WAIT
    CONF W

    # to left
    MOVE4_T X-200 Y200 Z80 P90 T1000
    WAIT
    CONF W

    # down
    MOVE4_T X-200 Y120 Z80 P90 T1000
    WAIT
    CONF W

    # release
    PWM Y110
    DELAY T300
    CONF W
    
    # up
    MOVE4_T X-200 Y200 Z80 P90 T1000
    WAIT
    CONF W


    GOTO loop





### returning to the local home
LABEL home

MOVE4_I X-200 Y200 Z0 P90
WAIT
CONF W
DELAY T500
CONF W

GOTO loop


EXIT