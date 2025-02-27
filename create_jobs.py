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


def update_joblist_files(job_base_name, joblist, full_header, joblist_archive_path="joblist_archive",update=True, force=False):
    """
    The Function will look for a joblist carrying the job_base_name in its path and then either 

        if the file already exists
            if update is True
                the function will overwrite the joblist completly
                if the same joblist was used to create the file in the first place
                then this functionality can be used to update the status of the joblist
            if update is False
                the function acts depending on the force attribute
                if force is True
                    the function will add all jobs in the joblist no matter if they are in the joblist already
                if force is False
                    the function will discard all jobs that are already in the joblist
                if force is none
                    the function will ask the user wheater jobs should be added
        if the file does not exist already
            the function will create the file and fill it with the joblist
    """
    target_joblist = f"{joblist_archive_path}/{job_base_name}_joblist.txt"
    inter_target_joblist = f"{joblist_archive_path}/inter_{job_base_name}_joblist.txt"

    # check wheater the joblist already exists and make content list
    if os.path.isfile(target_joblist):
        if not update:
            print(f"The file {target_joblist} already exists.\n")
            with open(target_joblist, 'r') as joblist_log:
                # make content list for easy file navigation
                joblist_log_content_list = [line for line in joblist_log.readlines()]

            # compare headers, if unfit, cancel operation
            header = joblist_log_content_list[1][:-2]
            if full_header == header:
                # open intermediate file to avoid data loss
                with open(inter_target_joblist, 'a') as inter_joblist_log:
                    # copy existing jobs
                    skipped_jobs = []
                    if not update:
                        for job_index in range(len(joblist_log_content_list)):
                            job_line = joblist_log_content_list[job_index]
                            inter_joblist_log.write(job_line)

                    # append new jobs
                    for job in joblist:
                        new_job_line = f"{str(list(job.values()))[1:-1]}\n"
                        # only append a job if it does not already exist
                        if new_job_line not in joblist_log_content_list or force==True:
                            inter_joblist_log.write(new_job_line)
                        else:
                            # keep track of skipped jobs
                            skipped_jobs.append((job['jobname'], job))

                    # if jobs were skipped, let user append them anyway
                    if force == None:
                        while len(skipped_jobs) != 0:
                            print("\nOne or more jobs were skipped. These jobs have probaply been done before.\n")
                            for jobname, job in skipped_jobs:
                                print(jobname, "\n")
                            instruction = input("\nDo you want to include these jobs anyway?[Y/n]\n")
                            if instruction == "Y":
                                for jobname, job in skipped_jobs:
                                    inter_joblist_log.write(f"{str(list(job.values()))[1:-1]} \n")
                                    print(f"{jobname} has been added to the joblist.")
                                break
                            elif instruction == "n":
                                break
                            else:
                                print("\nInvalid input, please restate your instruction!\n")
            else:
                print("Headers do not fit, please choose different base name")                    
        else:
            with open(target_joblist, 'r') as joblist_log:
                # make content list for easy file navigation
                joblist_log_content_list = [line for line in joblist_log.readlines()]
            header = joblist_log_content_list[1][:-2]
            if full_header == header:
                with open(inter_target_joblist, 'a') as inter_joblist_log:
                    #add the header
                    inter_joblist_log.write("HEADER,\n")
                    inter_joblist_log.write(f"{str(list(joblist[0].keys()))[1:-1]} \n")
                    inter_joblist_log.write("CONTENT,\n")
                    for job in joblist:
                        inter_joblist_log.write(f"{str(list(job.values()))[1:-1]} \n")

            else:
                print("Headers do not fit, please choose different base name")      

        # overwrite old joblist_log

        with open(target_joblist, 'w') as joblist_log:
            with open(inter_target_joblist, 'r') as inter_joblist_log:
                joblist_log.seek(0,0)
                new_joblist_log = inter_joblist_log.read()
                joblist_log.write(new_joblist_log)    

        # remove the inter_joblist
        os.remove(inter_target_joblist)

        # return that the operation was successfull
        return True
        
    else:
        with open(target_joblist, 'a') as joblist_log:
            #add the header
            joblist_log.write("HEADER,\n")
            joblist_log.write(f"{str(list(joblist[0].keys()))[1:-1]} \n")
            joblist_log.write("CONTENT,\n")
            for job in joblist:
                joblist_log.write(f"{str(list(job.values()))[1:-1]} \n")
        # return that the operation was successfull
        return True
    
def retrieve_joblist(base_name, characters_to_exclude=[" ", "'"]):
    """
    This function is used to create a joblist from a joblist.txt file. This way it is possible 
    to recover a simulation series in chase of technical failure and to not simulate something twice.
    """

    current_working_directory = os.getcwd()
    joblist_file_path = f"{current_working_directory}/joblist_archive/{base_name}_joblist.txt"

    with open(joblist_file_path, 'r') as joblist:
        joblist_content = [line for line in joblist]

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

    return joblist   

