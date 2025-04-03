import sys
import os

def make_tools(instructions):
    
    try:
        die_radius = instructions[1]
        jobname = instructions[2]
    except:
        pass
    
    with open(r"RectangularCupSingle.inp",'w') as file_rectangular_cup_input:
        file_rectangular_cup_input.write(f"60\n40\n3\n3\n20\n{die_radius}\n20\n1.1\n1")
    
    os.system('./RectangularCupSingle.exe < RectangularCupSingle.inp')
    os.rename('Tools.t52', f'{jobname}.t52')

instructions = sys.argv
make_tools(instructions)