import sys
import os

"""
This program will delete every file other than the ones specified in its instructions. It serves as a means to avoid file littering in the precessing directories.
This is important, because it can happen that simulation processes are not completed or create unforseen error files or such. If this happens repeadetly, the directories will overflow.
"""

def move_data(argument_vector):
    try:
        also_not_delete = argument_vector[1]
        also_not_type = argument_vector[2]
    except:
        print("Not all variables have been defined")
    
    files_not_to_delete_names = also_not_delete.split(' ')
    files_not_to_delete_suffixes = also_not_type.split(' ')

    current_working_directory = os.getcwd()
    files_in_directory = os.listdir(f"{current_working_directory}")

    for file in files_in_directory:
        if file in also_not_delete:
            continue
        try:
            file_suffix = file.split('.')[1]
            if file_suffix in files_not_to_delete_suffixes:
                continue
            os.remove(file)
        except:
            continue


        
instructions = sys.argv
move_data(instructions)