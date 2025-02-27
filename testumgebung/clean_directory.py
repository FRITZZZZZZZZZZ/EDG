import sys
import os

"""
This program will delete every file other than the ones specified in its instructions. It serves as a means to avoid file littering in the precessing directories.
This is important, because it can happen that simulation processes are not completed or create unforseen error files or such. If this happens repeadetly, the directories will overflow.
"""

def move_data(argument_vector):
    try:
        files_not_to_delete = argument_vector[1]
        file_types_not_to_delete = argument_vector[2]
    except:
        print("Not all variables have been defined")
    
    files_not_to_delete_names = files_not_to_delete.split(' ')
    files_not_to_delete_suffixes = file_types_not_to_delete.split(' ')

    current_working_directory = os.getcwd()
    files_in_directory = os.listdir(f"{current_working_directory}")

    for file in files_in_directory:
        if file in files_not_to_delete:
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