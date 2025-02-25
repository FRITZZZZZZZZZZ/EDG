import os

def create_jobs(job_base_name : str, valuelist_list: list, header : list, header_meta=["Jobname", "Status"], export_header=True):  
    """
    This function takes a job_base_name string, a valuelist_list containting lists conatining numbers, a header, a meta header and a boolean export header.
    The job_base_name will be used in every jobname and serve as a means to detect  jobs that belong to the same simulation series.
    The valuelist_list is a list made up of several individual lists containing number(floats and ints).
    The header is a list of strings, the strings are design parameter names.
    The header_meta carries the names of meta parameters such as the jobname and the stauts of a job.
    
    It is important that the valuelist_list and the header have the same number of entries.
    
    This function will construct a simulation series by generating a job for every possible combination of the design_parameter_values
    contained in the valuelist_list.
    
    After checking the validity of the input, the function will calculate the number of jobs in the simulation series.
    It does that by calculating the product over all lengths of the lists contained in the valuelist_list.
    This value n of the total number of jobs is then used to predifine n lists with the same length as the header.
    These lists will be filled with the design parameter values of the jobs.
    To fill the lists with values, the total number of jobs is divided by the number of values in the first value range of the valuelist_list.
        Since the total number of jobs is a product of this number of values in the value range, it is guaranteed that this will yield an integer number.
    """
    
    # define helper variables
    header_length = len(header)
    header_meta_length = len(header_meta)   

    # check input validity
    if len(valuelist_list) != len(header):
        print("Value ranges do not match header.")
        return 1

    # determine the number of jobs
    jobs_n = 1
    for value_list in valuelist_list:
        jobs_n *= len(value_list)    

    # create raw job lists in order for their indices to be addressable
    joblist = [[None for attribute in range(header_length + header_meta_length)] for job in range(jobs_n)]
    
    # fill raw job lists with values
    repetition_factor = jobs_n
    for attribute_index in range(header_length):
        value_list = valuelist_list[attribute_index]

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
    joblist_new = []
    for job_index in range(jobs_n):
        values = joblist[0]
        keys = header_meta + header
        job_dict = dict(zip(keys, values))
        joblist.append(job_dict)
        joblist = joblist[1:]

    attribute_nicknames = []
    for attribute in header:
        nickname_parts = attribute.split('_')
        attribute_nickname = ""
        for part in nickname_parts:
            attribute_nickname += part[0:2]
        attribute_nicknames.append(attribute_nickname)

    for job in joblist:
        quick_key = f"{job_base_name}"
        for attribute_index in range(len(header)):
            attribute = header[attribute_index]
            quick_key += "_" + attribute_nicknames[attribute_index] + "_" + str(job[attribute])
        job["Jobname"] = quick_key
        job["Status"] = "pending"
        
    if export_header:
        full_header = str(header_meta + header)[1:-1]
        return (joblist, full_header)
    else:
        return joblist

def update_joblist_files(job_base_name, joblist, full_header, joblist_archive_path="joblist_archive",update=True, force=False):
    """
    The Function will look for the joblist carrying the job_base_name in its path.
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
    
def retrieve_joblist(joblist_file, characters_to_exclude=[" ", "'"]):
    def string_list_cleanup(string_list, characters_to_exclude):
        for list_index in range(len(values)):
                value = values[list_index]
                clean_value = ""
                for letter in value:
                    if letter in characters_to_exclude:
                        continue
                    else:
                        clean_value += letter
                string_list[list_index] = clean_value
        return string_list
        
    with open(joblist_file, 'r') as joblist_log:
        joblist_log_content_list = [line for line in joblist_log]
        header = joblist_log_content_list[1][:-1].split("'")[1::2]
        joblist_log_data_list = joblist_log_content_list[3:]
        joblist = []
        for job_line in joblist_log_data_list:
            job = {}
            values = job_line[:-1].split(",")
            string_list_cleanup(values, characters_to_exclude)
            for attribute_index in range(len(header)):
                attribute = header[attribute_index]
                try:    
                    job[attribute] = float(values[attribute_index])
                except:
                    job[attribute] = values[attribute_index]
            joblist.append(job)

    return joblist   

