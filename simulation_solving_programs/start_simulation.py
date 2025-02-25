import sys
import os

def start_simulation(instructions): 

    try:
        jobname = instructions[1]
    except:
        pass
    
    os.system(f'./Indeed_1.0.3_ger_linux64.exe -j {jobname} -c 4 &')

instructions = sys.argv
start_simulation(instructions)