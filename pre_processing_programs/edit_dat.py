import sys
import os
import time

def edit_dat(argument_vector):
    # unpack argument vector
    try:
        property_keyword = argument_vector[1]
        target_index = argument_vector[2]
        element_keyword = argument_vector[3]        
        file_path_original = argument_vector[4]
        target_value = argument_vector[5]        
        jobname = argument_vector[6]        
    except:
        pass

    if os.path.exists(fr"{jobname}.dat"):
        with open(fr"{jobname}.dat", 'r') as file_original:
            content_original = [line for line in file_original]
    else:
        with open(file_path_original, 'r') as file_original:
            content_original = [line for line in file_original]

    content_edited = ""
    target_line_index = None
    with open(f"{jobname}.dat", 'w') as file_edited:
        for line_index in range(len(content_original)):
            if content_original[line_index][:-1] == element_keyword:
                if property_keyword in content_original[line_index + 1]:
                    keyword_line_length = len(content_original[line_index + 1])
                    target_line_index = line_index + 2
                    target_line = content_original[target_line_index][:-1]
                    target_line_list = target_line.split(',')                 
                    target_line_list[int(target_index)] = target_value
                    line_edited = ""
                    for item in target_line_list:
                        if item == ',' or item == '':
                            continue
                        line_edited = line_edited + str(item) + ","
                    
                    line_edited = line_edited + "\n"
            if not target_line_index == None and line_index == target_line_index:
                content_edited = content_edited[:-keyword_line_length]
                content_edited = content_edited + f"$ {property_keyword} = {target_value}\n"
                content_edited = content_edited + line_edited
            else:
                content_edited = content_edited + content_original[line_index] 
        file_edited.write(content_edited)

argument_vector = sys.argv
edit_dat(argument_vector)