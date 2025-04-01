import os

def create_jobs(job_base_name : str, value_range_list: list, header : list):  
    """
    This function takes a job_base_name string, a value_range_list containting lists conatining numbers, a header, a meta header and a boolean export header.
    The job_base_name will be used in every jobname and serve as a means to detect  jobs that belong to the same simulation series.
    The value_range_list is a list made up of several individual lists containing number(floats and ints).
    The header is a list of strings, the strings are design parameter names.
    The header_meta carries the names of meta parameters such as the jobname and the stauts of a job.
    
    It is important that the value_range_list and the header have the same number of entries.
    
    This function will construct a simulation series by generating a job for every possible combination of the design_parameter_values
    contained in the value_range_list.
    
    After checking the validity of the input, the function will calculate the number of jobs in the simulation series.
    It does that by calculating the product over all lengths of the lists contained in the value_range_list.
    This value n of the total number of jobs is then used to predifine n lists with the same length as the header.
    These lists will be filled with the design parameter values of the jobs.
    To fill the lists with values, the total number of jobs is divided by the number of values in the first value range of the value_range_list.
        Since the total number of jobs is a product of this number of values in the value range, it is guaranteed that this will yield an integer number.
    """
    
    # define the meta header
    header_meta=["Jobname", "Status"]

    # define helper variables
    header_length = len(header)
    header_meta_length = len(header_meta)   

    # check input validity
    if len(value_range_list) != len(header):
        print("Value ranges do not match header.")
        return False

    # determine the number of jobs
    jobs_n = 1
    for value_list in value_range_list:
        jobs_n *= len(value_list)    

    # create raw job lists in order for their indices to be addressable
    joblist = [[None for attribute in range(header_length + header_meta_length)] for job in range(jobs_n)]

    # fill raw job lists with values
    repetition_factor = jobs_n
    for attribute_index in range(header_length):
        value_list = value_range_list[attribute_index]

        job_attribute_index = header_meta_length + attribute_index
        repetition_factor /= len(value_list)
        cycle_factor = int(jobs_n / (len(value_list) * repetition_factor))

        job_index = 0
        for cycle in range(cycle_factor):
            for value in value_list:
                for repetition in range(int(repetition_factor)):
                    joblist[job_index][job_attribute_index] = value
                    job_index += 1

    # turn raw job lists into jobs
    for job_index in range(jobs_n):
        values = joblist[0]
        keys = header_meta + header
        job_dict = dict(zip(keys, values))
        joblist.append(job_dict)
        joblist = joblist[1:]
    
    # create shorthands for each attribute
    attribute_nicknames = []
    for attribute in header:
        nickname_parts = attribute.split(' ')
        attribute_nickname = ""
        for part in nickname_parts:
            attribute_nickname += part[0:2]
        attribute_nicknames.append(attribute_nickname)

    # write jobname and status into meta attributes
    for job in joblist:
        quick_key = f"{job_base_name}"
        for attribute_index in range(len(header)):
            attribute = header[attribute_index]
            quick_key += "_" + attribute_nicknames[attribute_index] + "_" + str(job[attribute])
        job["Jobname"] = quick_key
        job["Status"] = "pending"
        
    # return all information that is needed in the joblist file
    full_header = header_meta + header

    return (joblist, full_header, value_range_list)


def retrieve_joblist(base_name):
    """
    This function is used to create a joblist from a joblist.txt file. This way it is possible 
    to recover a simulation series in chase of technical failure and to not simulate something twice.
    """

    current_working_directory = os.getcwd()
    joblist_file_path = f"{current_working_directory}/joblist_archive/{base_name}_joblist.txt"
    
    try:
        with open(joblist_file_path, 'r') as joblist:
            joblist_content = [line for line in joblist]

        # find value ranges
        value_ranges_found = False
        value_name_next = False
        value_range_next = False
        value_names = []
        value_ranges = []
        for line in joblist_content:
            line = line[:-1]
            if line == "HEADER":
                break
            if line == "VALUE RANGES":
                value_name_next = True
                continue
            if value_name_next:
                value_names.append(line)
                value_name_next = False
                value_range_next = True
                continue
            if value_range_next:
                values = [float(value) for value in line.split(' ')]
                value_ranges.append(values)
                value_name_next = True
                value_range_next = False

        # find header
        header_found = False
        for line in joblist_content:
            line = line[:-1]
            if header_found:
                header = line.split(',')
                break
            if "HEADER" in line:
                header_found = True

        keys = header

        # make jobs
        job_value_list = []
        start_found = False
        for line in joblist_content:
            line = line[:-1]
            if "END DATA" in line:
                break
            if start_found:
                job_values = line.split(',')
                job_value_list.append(job_values)
            if "START" in line:
                start_found = True 
        joblist = []
        for value_list in job_value_list:
            job = dict(zip(keys, value_list))
            joblist.append(job)
        return joblist, header, value_ranges
    
    except:
        joblist = None



def update_joblist_files(job_base_name : str, job_tuple, overwrite=True):
    """
    This function can create and alter joblist files. Joblist files are used to keep track of simulation series and save time by documenting the work done
    and therefore prevent work to be carried out twice. It also helps finding errors or jobs that provoke errors and can be used to recover a simulation
    series in chase of technical failure.

    The function can be used to overwrite existing joblists by setting the overwrite option to True. This is done in order to update them, 
    for example if you want to set the status of a job to "in progress". 

    If overwrite is set to False the function will only ever add jobs to the joblist. This can be used if after a simulation series, you want to add some data to the dataset.
    """

    # define and unpack important variables and information
    current_working_directory = os.getcwd()
    joblist_file_path = f"{current_working_directory}/joblist_archive/{job_base_name}_joblist.txt"
    # try to unpack a three tuple in order to update the 
    joblist, header, value_ranges = job_tuple
    combined_joblist = []

    # look wheather the joblist file already exists
    if os.path.isfile(joblist_file_path) and not overwrite:

        # if the file does already exist, gather its content
        with open(joblist_file_path, 'r') as existing_joblist:
            existing_joblist_content = [line for line in existing_joblist.readlines()]
        
        # check the values range names of the joblist file 
        header_found = False
        file_fitting = False
        for line in existing_joblist_content:
            if header_found:
                existing_header = line[:-1].split(',')
                if existing_header == header:
                    file_fitting = True
                    break
                else:
                    print("Headers do not match.")
                    return False
            # mark the header to be found
            if "HEADER" in line:
                header_found = True
        
        # retrieve the existing joblist
        existing_joblist, header, value_ranges = retrieve_joblist(job_base_name)

        # combine the new and the old joblist
        combined_joblist = existing_joblist
        jobs_to_be_added = []
        for new_job in joblist:            
            if new_job in existing_joblist:
                continue
            else:
                jobs_to_be_added.append(new_job)       

    if not combined_joblist == []:
        joblist = combined_joblist
    
    # the file content is wirtten line by line into a content list first, the first entries of this list can be predefined as they follow a certain pattern
    content_list = ["NAME\n", f"{job_base_name}\n", "VALUE RANGES\n"]

    # write the value ranges to the joblist file, for this, the meta header must be ignored so the first two attributes are left out
    metaless_header = header[2:]
    for attribute_index in range(len(metaless_header)):
        range_name = metaless_header[attribute_index] + "\n"
        content_list.append(range_name)
        # turn the value range into a blank space delimited format
        value_range = value_ranges[attribute_index]
        value_range_string = ""
        for value in value_range:
            value_range_string += str(value) + " "
        value_range_string = value_range_string[:-1] + "\n"
        content_list.append(value_range_string)

    # create the header string
    content_list.append("HEADER\n")
    header_string = ""
    for attribuite in header:
        header_string += attribuite + ","
    # prune off the last semicolone and add a newline character to the header, then append
    header_string = header_string[:-1] + "\n"
    content_list.append(header_string)
    
    # now the start of the actual content starts
    content_list.append("START\n")

    # write the job data into the joblist
    for job in joblist:
        joblist_entry = ""
        for header_attribute in header:
            try:
                joblist_entry += job[header_attribute] + ","
            except:
                joblist_entry += str(job[header_attribute]) + ","
        joblist_entry = joblist_entry[:-1] + "\n"   
        content_list.append(joblist_entry)

    # the content list definition is done, mark the end of the file
    content_list.append("END DATA\n")

    # create one big string from the content list, maybe one could start out using strings, but using lists seems more flexible
    joblist_content = ""
    for line in content_list:
        joblist_content += line

    # write all job vlaues to the content list
    with open(f"{current_working_directory}/joblist_archive/{job_base_name}_joblist.txt", 'w') as new_joblist_file:
        new_joblist_file.write(joblist_content)
