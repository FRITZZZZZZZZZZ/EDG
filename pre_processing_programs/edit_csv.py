import sys
import os

def edit_csv(argument_vector):
    # retrieve arguments
    try:    
        header_raw = argument_vector[1]
        target_attribute = argument_vector[2]
        target_value_constraint = argument_vector[3]
        length_csv_keyword = argument_vector[4]
        start_index_csv_keyword = argument_vector[5]
        file_original_path = argument_vector[6]
        target_value = argument_vector[7]        
        jobname = argument_vector[8]        
    except:
        pass
    
    # turn the header into an actual list
    header = header_raw[1:-1].split(' ')



    # load file
    if os.path.exists(fr"{jobname}.t51"):
        with open(fr"{jobname}.t51", 'r') as file_original:
            original_content = [line for line in file_original]
    else:
        with open(file_original_path, 'r') as file_original:
            original_content = [line for line in file_original]

    # get csv data
    pre_csv = ""
    csv_content = []
    csv_index = 0
    line_n_pre_csv = 0
    for line_index in range(len(original_content)):
        current_line = original_content[line_index]
        pre_csv = pre_csv + current_line
        line_n_pre_csv += 1
        if length_csv_keyword in current_line:
            csv_length = int(original_content[line_index + 1][:-2])
        if start_index_csv_keyword in current_line:
            csv_start_index = line_index +1
            current_line = original_content[csv_start_index]
            for csv_index in range(csv_length):
                current_line = original_content[csv_start_index + csv_index]
                csv_content.append(current_line)
            break
    
    # check header match
    try:
        first_entry_list = csv_content[0][:-3].split(',')
        if len(first_entry_list) == len(header):
            pass
        else:
            print("\nHeader does not fit CSV data.\n")
            return 1
    except:
        return 1
    
    # get index of data to be modified
    for header_index in range(len(header)):
        if header[header_index] == target_attribute:
            attribute_index = header_index

    # modify csv
    i = 0
    csv_edited = ""
    for entry_index in range(len(csv_content)):
        entry = csv_content[entry_index]
        entry_list = entry.split(',')
        target_attribute_value = float(entry_list[attribute_index])
        if target_attribute_value == target_value_constraint:
            entry_list[attribute_index] = target_value
        entry_edited = ""
        for item in entry_list:  
            if item == " ":
                continue
            entry_edited = entry_edited + str(item) + ","
        csv_edited = csv_edited + entry_edited[:-1]

    post_csv = ""
    start_post_csv_index = line_n_pre_csv + csv_length
    remainder = original_content[start_post_csv_index:]
    for line in remainder:
        post_csv = post_csv + line
    
    edited_content = pre_csv + csv_edited + post_csv

    with open(f"{jobname}.t51", "w") as file_edited:
        file_edited.write(edited_content)
    
instruction = sys.argv
edit_csv(instruction)

