# cpp: 
# for (int i = 0; i < 10; i++) {
#    # code
# }

# fpp:
VAL i: int= 0
LABEL start
IF (i < 10)
    GOTO end
    # code
    INC i
    GOTO start
LABEL end

EXIT