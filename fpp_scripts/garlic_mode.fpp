

VAL int height = 350
VAL int time = 2000

VAL int enable = 0

LABEL loop

    IF (btn0 == 1)
        GOTO if0
        VAL btn0 = 0

        PRINT "btn 0 pressed"

        MOVE4_T X0 Y150 Z-300 P0 T=time
        WAIT
        CONF W

        VAL height = 250
        VAL time = 1000

    LABEL if0

    IF (btn1 == 1)
        GOTO if1
        VAL btn1 = 0

        MOVE4_T X0 Y150 Z-300 P0 T=time
        WAIT
        CONF W

        PRINT "btn 1 pressed"
        VAL height = 350
        VAL time = 2000

    LABEL if1

    IF (btn2 == 1)
        GOTO if2
        VAL btn2 = 0

        PRINT "btn 2 pressed"
        PRINT enable
        PRINT "btn 2 pressed22222"

        IF (enable == 0)
            GOTO set
            VAL enable = 1
            PRINT "set"
            GOTO if2
        LABEL set
        IF (enable == 1)
            GOTO reset
            VAL enable = 0
            PRINT "reset"
            GOTO if2
        LABEL reset


    LABEL if2


    IF (enable == 1)
        GOTO end_move

        MOVE4_T X0 Y150 Z-300 P0 T=time
        WAIT
        CONF W

        MOVE4_T X0 Y=height Z-300 P0 T=time
        WAIT
        CONF W

    LABEL end_move

GOTO loop

EXIT


