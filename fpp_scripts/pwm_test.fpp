

PWM Y87
CONF

EXIT

LABEL loop


    IF (btn0 == 1)
        GOTO if0
        VAL btn0 = 0

        PRINT "btn 0 pressed"

        GOTO open

    LABEL if0

    IF (btn1 == 1)
        GOTO if1
        VAL btn1 = 0

        PRINT "btn 1 pressed"

        GOTO mid

    LABEL if1

    IF (btn2 == 1)
        GOTO if2
        VAL btn2 = 0

        PRINT "btn 2 pressed"

        GOTO close
    
    LABEL if2

GOTO loop


### open ###
LABEL open
PWM Y100
CONF
GOTO loop

### close ###
LABEL close
PWM Y50
GOTO loop

### mid ###
LABEL mid
PWM Y87
CONF
GOTO loop
