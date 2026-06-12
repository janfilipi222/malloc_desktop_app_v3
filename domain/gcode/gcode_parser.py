from domain.gcode.fpp_commands import *
from domain.gcode.instruction_lookup import InstructionLookup
import math
import re


class GCodeParser:
    def parse(self, lines: list[str]) -> list[FppCommand]:

        # print("parsing: ", lines)

        commands: list[FppCommand] = []

        for line in lines:
            line = line.strip()


            if not line or line.startswith("#"):
                continue

            parts = line.split()
            cmd = parts[0]

            print(parts)

            # PHYSICAL COMMANDS

            if cmd == InstructionLookup.ROTATE.value:
                for p in parts[1:]:
                    if p.startswith("I"):
                        index = int(p[1:])
                    elif p.startswith("S"):
                        steps = int(p[1:])
                commands.append(MoveJoint(index, steps))

            elif cmd == InstructionLookup.WAIT.value:
                commands.append(WaitTillDone())
                
            elif cmd == InstructionLookup.DELAY.value:
                for p in parts[1:]:
                    if p.startswith("T"):
                        time = p[1:]
                commands.append(DelayMs(time))

            elif cmd == InstructionLookup.MOVE_4_TIMED.value:
                wait = False
                for p in parts[1:]:
                    if p.startswith("X"):
                        x = p[1:]
                    if p.startswith("Y"):
                        y = p[1:]
                    if p.startswith("Z"):
                        z = p[1:]
                    if p.startswith("P"):
                        pitch = p[1:]
                    if p.startswith("T"):
                        time = p[1:]
                    if p.startswith("W"):
                        wait = True
                commands.append(GoToPos4DOFTimed(x, y, z, pitch, time, wait))

            elif cmd == InstructionLookup.MOVE_4_IND.value:
                wait = False
                for p in parts[1:]:
                    if p.startswith("X"):
                        x = p[1:]
                    if p.startswith("Y"):
                        y = p[1:]
                    if p.startswith("Z"):
                        z = p[1:]
                    if p.startswith("P"):
                        pitch = p[1:]
                    if p.startswith("W"):
                        wait = True
                commands.append(GoToPos4DOFIndependent(x, y, z, pitch, wait))

            elif cmd == InstructionLookup.MOVE_45_TIMED.value:
                wait = False
                x = y = z = pitch = a = t = 0
                for p in parts[1:]:
                    if p.startswith("X"):
                        x = p[1:]
                    if p.startswith("Y"):
                        y = p[1:]
                    if p.startswith("Z"):
                        z = p[1:]
                    if p.startswith("P"):
                        pitch = p[1:]
                    if p.startswith("A"):
                        a = p[1:]
                    if p.startswith("T"):
                        t = p[1:]
                    if p.startswith("W"):
                        wait = True
                print("parsing T:", t)
                commands.append(GoTo4dot5DOFTimed(x, y, z, pitch, a, t, wait))

            elif cmd == InstructionLookup.MOVE_33_MANUAL_TIMED.value:
                x = y = z = a = b = c = 0
                wait = False
                for p in parts[1:]:
                    if p.startswith("X"):
                        x = int(p[1:])
                    if p.startswith("Y"):
                        y = int(p[1:])
                    if p.startswith("Z"):
                        z = int(p[1:])
                    if p.startswith("A"):
                        a = int(p[1:])
                    if p.startswith("B"):
                        b = int(p[1:])
                    if p.startswith("C"):
                        c = int(p[1:])
                    if p.startswith("T"):
                        t = int(p[1:])
                    if p.startswith("W"):
                        wait = True
                commands.append(GoToPos3DOF3ManualTimed(x, y, z, a, b, c, t, wait))
    
            elif cmd == InstructionLookup.MOVE_33_MANUAL_TIMED.value:
                x = y = z = p = y = r = 0
                wait = False
                for p in parts[1:]:
                    if p.startswith("X"):
                        x = int(p[1:])
                    if p.startswith("Y"):
                        y = int(p[1:])
                    if p.startswith("Z"):
                        z = int(p[1:])
                    if p.startswith("P"):
                        p = int(p[1:])
                    if p.startswith("Y"):
                        y = int(p[1:])
                    if p.startswith("R"):
                        r = int(p[1:])
                    if p.startswith("T"):
                        t = int(p[1:])
                    if p.startswith("W"):
                        wait = True
                commands.append(GoToPos3DOF3ManualTimed(x, y, z, p, y, r, t, wait))
   
            elif cmd == InstructionLookup.CONFIRM.value:
                wait = False
                for p in parts[1:]:
                    if p.startswith("W"):
                        wait = True
                commands.append(Confirm(wait))


            # FLOW COMMANDS

            elif cmd == InstructionLookup.EXIT.value:
                break

            elif cmd == InstructionLookup.HOME.value:
                commands.append(GoHome())

            elif cmd == InstructionLookup.PWM.value:
                for p in parts[1:]:
                    if p.startswith("X"):
                        channel = "x"
                        value = p[1:]
                    if p.startswith("Y"):
                        channel = "y"
                        value = p[1:]
                commands.append(MovePWM(channel, value))


            # FPP

            elif cmd == InstructionLookup.VAL.value:  
                p = parts
                print("parsing", p)

                index = 0

                if (p[1] == "int" or
                    p[1] == "float" or
                    p[1] == "str"):
                    index = 1
                    type = p[index]
                else:
                    type = "int"

                index += 1
                name = p[index]
                index += 2
                value = p[index]

                commands.append(Value(name, type, value))

            elif cmd == InstructionLookup.GOTO.value:
                commands.append(GoTo(label_name=parts[1]))
        
            elif cmd == InstructionLookup.LABEL.value:
                commands.append(Label(label_name=parts[1]))

            elif cmd == InstructionLookup.INCREMENT.value:
                p = parts
                commands.append(Increment(variable_name=p[1]))
            
            elif cmd == InstructionLookup.CONDITION.value:
                expr = re.search(r"\((.*?)\)", line)
                commands.append(Condition(expr.group(1)))

            elif cmd == InstructionLookup.PRINT.value:
                if line.find("\"") > -1:
                    value = "\"" + line.split('"')[1] + "\""
                else:
                    value = parts[1]
                commands.append(Print(value))

            elif cmd == InstructionLookup.CALCULATE.value:
                commands.append(Calculate(parts[1], parts[3], parts[5], parts[4]))
                



        print(commands)

        return commands




