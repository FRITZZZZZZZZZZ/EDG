import sys
import os

def scale_blank(instructions):
    try:
        dimension = instructions[1]
        factor = instructions[2]
        jobname = instructions[3]
    except:
        pass

    scale_x = 1
    scale_y = 1
    scale_z = 1

    if dimension == "x":
        scale_x =  factor
    elif dimension == "y":
        scale_y = factor
    elif factor == "z":
        scale_z = factor

    with open('scaling_input.inp', 'w') as scaling_input_file:
        scaling_input_file.write(f"{jobname}\n{scale_x} {scale_y} {scale_z}")
    os.system("./ScaleGeometry.exe < scaling_input.inp")

instructions = sys.argv
scale_blank(instructions)
