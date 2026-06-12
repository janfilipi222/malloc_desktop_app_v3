
VAL close = 75
VAL open = 100
VAL new_cam_data = 0
PWM Yopen

VAL time = 2000
VAL delay = 1000

LABEL loop

    IF (btn0 == 1)
    GOTO if_btn_0

        VAL btn0 = 0
        PRINT "btn0 press"
        MOVE4_I X0 Y200 Z-250 P90
        WAIT
        CONF W

    LABEL if_btn_0

    IF (new_cam_data > 0)
    GOTO main_if
        PRINT "new data"

        # init move
        MOVE4_T X=-200 Y200 Z=00 P90 T5000
        WAIT
        CONF W

        # move above the first box
        MOVE44_T X=box0_y Y200 Z=box0_x P90 A=box0_a Ttime
        WAIT
        CONF W
        #DELAY T1000
        #CONF W

        # move down
        MOVE44_T X=box0_y Y100 Z=box0_x P90 A=box0_a Ttime
        WAIT
        CONF W
        #DELAY T1000
        #CONF W

        # pick up box
        PWM Yclose
        DELAY T500
        CONF W

        # move up
        MOVE4_T X=box0_y Y200 Z=box0_x P90 Ttime
        WAIT
        CONF W
        #DELAY T1000
        #CONF W

        # go to tower place
        MOVE4_T X-200 Y200 Z0 P90 Ttime
        WAIT
        CONF W
        #DELAY T1000
        #CONF W
        
        # place first box
        MOVE4_T X-200 Y100 Z0 P90 Ttime
        WAIT
        CONF W
        #DELAY T1000
        #CONF W

        # release first box
        PWM Yopen
        DELAY T500
        CONF W

        # move up
        MOVE4_T X-200 Y200 Z0 P90 Ttime
        WAIT
        CONF W
        #DELAY T1000
        #CONF W

        # checks if there is second box
        IF (new_cam_data > 1)
        GOTO if_second_box


            # move above the second box
            MOVE44_T X=box1_y Y200 Z=box1_x P90 A=box1_a Ttime
            WAIT
            CONF W
            #DELAY T1000
            #CONF W

            # move down
            MOVE44_T X=box1_y Y100 Z=box1_x P90 A=box1_a Ttime
            WAIT
            CONF W
            #DELAY T1000
            #CONF W

            # pick up box
            PWM Yclose
            DELAY T500
            CONF W

            # move up
            MOVE4_T X=box1_y Y200 Z=box1_x P90 Ttime
            WAIT
            CONF W
            #DELAY T1000
            #CONF W

            # go to tower place
            MOVE4_T X-200 Y200 Z0 P90 Ttime
            WAIT
            CONF W
            #DELAY T1000
            #CONF W
            
            # place second box
            MOVE4_T X-200 Y116 Z0 P90 Ttime
            WAIT
            CONF W
            #DELAY T1000
            #CONF W

            # release second box
            PWM Yopen
            DELAY T500
            CONF W

            # move up
            MOVE4_T X-200 Y200 Z0 P90 Ttime
            WAIT
            CONF W
            #DELAY T1000
            #CONF W

            IF (new_cam_data > 2)
            GOTO if_third_box


                # move above the third box
                MOVE44_T X=box2_y Y200 Z=box2_x P90 A=box2_a Ttime
                WAIT
                CONF W
                #DELAY T1000
                #CONF W

                # move down
                MOVE44_T X=box2_y Y100 Z=box2_x P90 A=box2_a Ttime
                WAIT
                CONF W
                #DELAY T1000
                #CONF W

                # pick up box
                PWM Yclose
                DELAY T500
                CONF W

                # move up
                MOVE4_T X=box2_y Y200 Z=box2_x P90 Ttime
                WAIT
                CONF W
                #DELAY T1000
                #CONF W

                # go to tower place
                MOVE4_T X-200 Y200 Z0 P90 Ttime
                WAIT
                CONF W
                #DELAY T1000
                #CONF W
                
                # place third box
                MOVE4_T X-200 Y132 Z0 P90 Ttime
                WAIT
                CONF W
                #DELAY T1000
                #CONF W

                # release third box
                PWM Yopen
                DELAY T500
                CONF W

                # move up
                MOVE4_T X-200 Y200 Z0 P90 Ttime
                WAIT
                CONF W
                #DELAY T1000
                #CONF W



            LABEL if_third_box

        LABEL if_second_box


        # go back to friendly photo pos
        MOVE4_T X=-200 Y200 Z=0 P90 Ttime
        WAIT
        CONF W


        VAL new_cam_data = 0
    LABEL main_if



GOTO loop

EXIT

PWM Yopen
CONF

MOVE4_T X0 Y200 Z-180 P90 T2000
WAIT
CONF W
DELAY T1000
CONF W


MOVE4_T X0 Y100 Z-250 P90 T2000
WAIT
CONF W
DELAY T1000
CONF W


PWM Ycls
CONF
