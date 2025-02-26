import sys
import os
import shutil

"""
This programm takes a path and a jobname as its input and moves all files containing 
the jobname to a certain location specified by the given path. It is the last step in 
a pre processing phase
"""

def move_data(argument_vector):
    delete = False
    try:
        file_types = argument_vector[1]
        target_folder_path = argument_vector[2]
        jobname = argument_vector[3]
        delete = argument_vector[4]
    except:
        print("Not all variables defined")
    
    file_type_list = file_types.split(' ')

    for file_type in file_type_list:
        try:
           # print(os.path.isfile(f"{jobname}.{file_type}"), "DAS WAR FÜR ", f"{jobname}{file_type}")
            print(file_type)
            shutil.move(f"{jobname}.{file_type}", f"{target_folder_path}")
        except:
            if delete == "else_delete":
                os.remove(f"{jobname}.{file_type}")
            print(f"Could not move {jobname}.{file_type}.")
            
        
instructions = sys.argv
move_data(instructions)