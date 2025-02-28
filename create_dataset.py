import os
import create_jobs

def create_dataset(base_name, design_parameter_names, csv_result_inline_keywords, csv_result_nextline_keywords, csv_header,include_header=True):
    
    # define important variables
    current_working_directory = os.getcwd() 
    joblist_file_path = f"{current_working_directory}/joblist_archive/{base_name}_joblist.txt"
    csv_result_directory_path = f"{current_working_directory}/raw_results/results_csv/{base_name}"

    # look through the directory and find all file names
    try:
        csv_result_file_names = os.listdir(csv_result_directory_path)
    except:
        print("No csv files to bundle up.")
        return False
    joblist = create_jobs.retrieve_joblist(joblist_file_path)  

    data_set_lines = []

    for file_name in csv_result_file_names:
        
        # declaring a new data set line
        data_set_line = ""

        # get the jobname by not including the .csv suffix
        jobname_csv = file_name[:-4]

        # find the related job in the joblist
        for job in joblist:
            jobname = job['Jobname']
            if jobname == jobname_csv:
                related_job = job
                break

        # retrieve the design parameters from the related job and append them to the data set line
        for design_parameter_name in design_parameter_names:
            data_set_line += str(related_job[design_parameter_name]) + ","
        
        # retrieve the results from the csv 
        with open(f"{csv_result_directory_path}/{file_name}", 'r') as csv_result_file:
            csv_result_content = [line for line in csv_result_file]
        
        # go through the result lines and gather all inline results, these results are at the end of the line containing the inline keyword
        for result_line in csv_result_content:
            result_line = result_line[:-1]
            for inline_keyword in csv_result_inline_keywords:
                if inline_keyword in result_line:
                    result_line_list = result_line.split(',')
                    result = str(float(result_line_list[-1]))
                    data_set_line += result + ","
        
        # go through the result lines and catch all nextline results, these results are a full line and not at the end of a line
        for result_line_index in range(len(csv_result_content)):
            result_line = csv_result_content[result_line_index]
            for nextline_keyword in csv_result_nextline_keywords:
                if nextline_keyword in result_line:
                    nextline = csv_result_content[result_line_index + 1]
                    nextline_list = nextline.split(',')
                    for nextline_result in nextline_list:
                        result = str(float(nextline_result))
                        data_set_line += result + ","
        
        # prune off the last semicolone, append a newline character and append the new dataset line to the data set line list
        data_set_line = data_set_line[:-1]
        data_set_line += "\n"
        data_set_lines.append(data_set_line)

    # create the new dataset csv file, if wished so append a header to it
    if include_header:
        dataset_first_lines = ["NAME\n", f"{base_name}\n","HEADER\n"] 
        full_header_string = ""
        full_header_list = design_parameter_names + csv_header
        for attribute in full_header_list:
            full_header_string += str(attribute) + ","
        full_header_list = full_header_string[:-1]
        full_header_string += "\n"
        dataset_first_lines.append(full_header_string)
        dataset_first_lines.append("START\n")
        data_set_lines = dataset_first_lines + data_set_lines

    # turn the line list into a string
    data_set_string = ""
    for line in data_set_lines:
        print(line)
        data_set_string += line
    
    if include_header:
        data_set_string += "END DATA"
    
    # write the string to a file
    with open(f"{current_working_directory}/complete_datasets/{base_name}.csv", 'w') as job_dataset:
        job_dataset.write(data_set_string)
    
    return True

