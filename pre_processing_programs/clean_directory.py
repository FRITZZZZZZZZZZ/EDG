import sys
import os


def clean_directory(argument_vector):
    """
    This program will delete every file other than the ones specified in its instructions. It serves as a means to avoid file littering in the precessing directories.
    This is important, because it can happen that simulation processes are not completed or create unforseen error files or such. If this happens repeadetly, the directories will overflow.
    """
    try:
        raw_files_to_spare = argument_vector[1]
    except:
        print("Not all variables have been defined")
    
    files_to_spare = raw_files_to_spare.split(' ')
    protected_suffixes = ['py', 'exe', 'mbl', 'tsv', 'csv', 'png', 'ofs', '']

    current_working_directory = os.getcwd()
    files_in_directory = os.listdir(f"{current_working_directory}")

    for file in files_in_directory:
        if file in files_to_spare:
            continue
        try:
            file_suffix = file.split('.')[1]
            if file_suffix in protected_suffixes:
                continue
            os.remove(file)
        except:
            continue

instructions = sys.argv
clean_directory(instructions)