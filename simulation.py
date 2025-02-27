import job_management
import os
import time
import interaction

def pick_interpreter(interpreter_tuple, command=None):
    """"
    This program takes a command and matched it to the right interpreter, it a interpreter list is passed.
    """
    if not interpreter_tuple == None and not command == None:
        interpreters, interpreter_suffixes = interpreter_tuple
        program_call = command.split(' ')[0]
        language_suffix = program_call.split('.')[1]
        for suffix in interpreter_suffixes:
            if language_suffix == suffix:
                interpreter = interpreters[suffix]
            else:
                # if the suffix is unknown try running the program as is
                interpreter = ''
    else:
        interpreter = "python"

def get_allowed_files_command():
    allowed_files = os.listdir()
    allowed_files_command = ""
    for file in allowed_files:
        allowed_files_command += file + " "
    allowed_files_command = "'" + allowed_files_command[:-1] + "'"
    return allowed_files_command

def pre_processing(job, editing_tuple, interpreter_tuple=None, pre_processing_time_out=60):
    """
    This function takes care of the pre processing of the simulation. It alters input files like dat t51 and t52
    and then moves them to the next step.
    """
    # unpack control data tuples
    control_commands, design_parameter_names = editing_tuple
    if not interpreter_tuple == None:
        interpreters, interpreter_suffixes = interpreter_tuple
    jobname = job["Jobname"]

    # remember the current working directory
    current_working_directory = os.getcwd()

    # change the current working directory to the one housing the pre processing methods
    success = None

    # prepare simulation by editing job data for every design parameter
    os.chdir(f"{current_working_directory}/pre_processing_programs/")

    # keep track of which files should be in this directory, so the cleanup function doesnt make too many casulties
    allowed_files = get_allowed_files_command()

    for parameter in design_parameter_names:

        # catch the comand and job
        value = job[parameter]
        command = control_commands[parameter]
        try:
            # match the program call with the right interpreter if wished so
            interpreter = pick_interpreter(interpreter_tuple, command)
            os.system(f"{interpreter} {command} {value} {jobname}")
        except:
            # if the program call did not work, something was not edited, dont continue the simulation and waste time
            os.system(f"python clean_directory.py {allowed_files}")
            os.chdir(f"{current_working_directory}/")
            success = False
            return success

    # if the pre processing was successful, the files will be transfered to the next step
    os.system(f"python move_data.py 'dat t51 t52' {current_working_directory}/simulation_solving_programs {jobname} else_delete")

    # clean up the directory, leave only allowed files here
    os.system(f"python clean_directory.py {allowed_files}")

    os.chdir(f"{current_working_directory}/")
    success = True
    return success

def solving_simulation(job, solve_tuple, interpreter_tuple=None, time_limit=900, loop_limit=5):

    def check_done(jobname, done_keyword):
        try:
            with open(rf"{jobname}.inf", 'r') as log_file:
                log_content = [line for line in log_file]
                log_content_length = len(log_content)
            for line_index in range(log_content_length):
                if done_keyword in log_content[log_content_length-1-line_index]:
                    return True
            return False
        except: 
            return False
        
    def check_loops(jobname, loop_limit, loops_passed, current_length, last_length, last_increment):
        """
        This is simple programm than can detect loops in a simulation and terminate it.
        """

        if not loop_limit == None:
            # check wheather the loop limit has been reached
            if loops_passed >= loop_limit:
                return True
            # read the inf file
            with open(rf"{jobname}.inf", 'r') as inf_file:
                inf_content = [line for line in inf_file]
                last_length = current_length
                current_length = len(inf_content)
            # look if there were lines edited to the file, only then compare the lines
            if current_length > last_length:
                refreshed = True
            else:
                refreshed = False

            # look through the lines in reverse to not get thorwn off by an empty line
            for line_index in range(len(inf_content)):
                
                line = inf_content[(len(inf_content)-1)-line_index]
                if "\n" in line:
                    line_list = line[:-1].split(' ')
                else:
                    line_list = line.split(' ')
                # if the line has the word INCREMENT in it
                if "INKREMENT" in line_list and refreshed == True:
                    # the increment number is the last element in this list
                    current_increment = line_list[-1]
                    # if the increment number is already present, note that it is now present one more time
                    if current_increment == last_increment:
                        loops_passed += 1
                        refreshed = False
                        line_list = []
                    else:
                        # if that isnt the chase and the increment number is a new one, update the last increment value
                        last_increment = current_increment
                        loops_passed = 0
                        refreshed = False
                        line_list = []
                    break

            return (loops_passed, current_length, last_length, last_increment)
    
    
    # unpack solve tuple, yes this seems quite inefficient but doing it that way is one way to make the control_file more human readable
    solving_commands, solving_commands_names = solve_tuple
        # start command
    start_command = solving_commands[solving_commands_names[0]]
        # keywords for stopping the simulation and for when the simulation is done
    done_keyword = solving_commands[solving_commands_names[1]]
    stop_command  = solving_commands[solving_commands_names[2]]
        # the list of file types to be transfered to post processing, this is a blank space delimited list in string format
    export_file_types = solving_commands[solving_commands_names[3]].split(' ')
    # more important variables
    jobname = job['Jobname']
    inf_file = None
    log_file = None

    # change the working directory to the one taking care of solving the simulation
    current_working_directory = os.getcwd()
    os.chdir(f"{current_working_directory}/simulation_solving_programs/")

    # keep track of which files should be in this directory, so the cleanup function doesnt make too many casulties
    allowed_files = get_allowed_files_command()

    # start the simulation
    interpreter = pick_interpreter(interpreter_tuple, start_command)
    os.system(f"{interpreter} {start_command} {jobname}")

    # wait for files to be available
    while inf_file == None or log_file == None:
        time.sleep(1)
        try:
            with open(rf"{jobname}.inf", 'r') as inf_file:
                current_length = len([line for line in inf_file.readlines()])
                last_length = current_length 
                inf_file = rf"{jobname}.inf"
            with open(rf"{jobname}.log", 'r') as log_file:
                log_file = rf"{jobname}.log"
        except:
            pass

    # keep track of simulation 
    success = None
    loops_passed = 0
    time_passed = 0
    last_increment = None

    # check for termination constraints
    while success == None:
        time.sleep(1)

        # check wheather the simulation is success
        if check_done(jobname, done_keyword):
            success = True
        
        # check wheather the simulation exceeded its loop limit
        check_loops_result = check_loops(jobname, loop_limit, loops_passed, current_length, last_length, last_increment)
        if type(check_loops_result) == tuple:
            loops_passed, current_length, last_length, last_increment = check_loops_result

        if type(check_loops_result) == bool:
            success = False    

        # check wheather the time is exceeded
        if not time_limit == None:
            if time_passed >= time_limit:
                success = False
            else:
                time_passed += 1

    if success == False:
        os.system(f"{stop_command}")
        os.system(f"python move_data.py {export_file_types} {current_working_directory}/post_processing_programs {jobname}")
        # clean up the directory, leave only allowed files here
        os.system(f"python clean_directory.py {allowed_files}")
        os.chdir(f"{current_working_directory}/")

    os.system(f"python move_data.py {export_file_types} {current_working_directory}/post_processing_programs {jobname}")
    # clean up the directory, leave only allowed files here
    os.system(f"python clean_directory.py {allowed_files}")
    os.chdir(f"{current_working_directory}/")

    return success
  
def post_processing(job, base_name, solving_success, post_tuple, interpreter_tuple, post_processing_time_out=180):
    # define important variables
    jobname = job['Jobname']
    post_commands, post_command_names = post_tuple   
    file_categories, category_names = clean_up_tuple
    current_working_directory = os.getcwd()

    # change the working directory to carry out work in the post processing environment
    os.chdir(f"{current_working_directory}/post_processing_programs/")
    new_working_directory = os.getcwd()

    # keep track of which files should be in this directory, so the cleanup function doesnt make too many casulties
    allowed_files = get_allowed_files_command()

    try:
        if solving_success:   
            
            # use the post processing programs to gather desired data and data formats from the simulation
            time_passed = 0 
            for post_command_name in post_command_names:
                command = post_commands[post_command_name]
                # pick the right interpreter to allow use of custom programs
                interpreter = pick_interpreter(interpreter_tuple, command)
                os.system(f"{interpreter} {command} {jobname}")

                # wait for open form to export the desired file formats.                 
                while time_passed <= post_processing_time_out:

                    # This is done via time out because open form is a different process and can take some time
                    n_files = len(os.listdir(new_working_directory))
                    time.sleep(1)
                    new_n_files = len(os.listdir(new_working_directory))
                    if new_n_files > n_files:
                        break
                    time_passed += 1
                    if time_passed >= post_processing_time_out:
                        os.chdir({current_working_directory})
                        print(f"{command} did not work.")
                        return False

            # sort the results according to the fact that the solving has been successful
                # all categories but the last one do define data types and their destined directories for successful solving
                # the very last one is reserved for the directory that stores the files of unsuccessful solving attempts
            success_categories = category_names[:-1]
            for category in success_categories:
                file_types, result_path = file_categories[category]
                # if the directory doesnt exist, create the directory to avoid "dIrEcToRY dOEsN'T eXiST" errors
                if not os.path.isdir(f"{current_working_directory}/{result_path}/{base_name}/"):
                    os.mkdir(f"{current_working_directory}/{result_path}/{base_name}/")
                # move the files to their destination folder
                os.system(f"python move_data.py {file_types} {current_working_directory}/{result_path}/{base_name} {jobname}")
        
        if not solving_success:

            # only the last category deals with files of unsuccessful solving attempts
            error_categories = category_names[-1]
            for category in error_categories:
                file_types, result_path = file_categories[category]
                # if the directory doesnt exist, create the directory to avoid "dIrEcToRY dOEsN'T eXiST" errors
                if not os.path.isdir(f"{current_working_directory}/{result_path}/{base_name}/"):
                    os.mkdir(f"{current_working_directory}/{result_path}/{base_name}/")
                # move the files to the folder storing the data of unsuccessful solving atttempts
                os.system(f"python move_data.py {file_types} {current_working_directory}/{result_path}/{base_name} {jobname}")

    except:
        # clean up the directory, leave only allowed files here
        os.system(f"python clean_directory.py {allowed_files}")
        os.chdir(f"{current_working_directory}")
        return False

    # clean up the directory, leave only allowed files here
    os.system(f"python clean_directory.py {allowed_files}")
    os.chdir(f"{current_working_directory}")
    return True


def run_simulation_series(base_name, joblist_tuple, pre_tuple, solve_tuple, post_tuple, time_limit=900, loop_limit=10, interpreter_tuple=None):

    # defining important control variables
    joblist, full_header, value_range_list = joblist_tuple
    ready = True

    for job_index in range(len(joblist)):
        if ready:
            
            # to avaid rushing threy the loop, this happened at production, who knows what caused it, this way it will definitly not happen again
            ready = False
            # pick a job from the joblist and mark its joblist entry as in progress
            job = joblist[job_index]

            # check the jobs status and see if the job is pending, if not, go to the next one
            if not job['Status'] == 'pending':
                ready = True
                continue

            else:
                job['Status'] = "in_progress"
                joblist_tuple = (joblist, full_header, value_range_list)
                job_management.update_joblist_files(base_name, joblist_tuple, full_header)

                # try solving the job
                try:
                    # start the preprocessing and prepare the input data
                    success_pre_processing = pre_processing(job, pre_tuple, interpreter_tuple, interpreter_tuple)
                    
                    # start the simulation once the preprocessing was succcsessful, append to error list else
                    if success_pre_processing:
                        success_solving = solving_simulation(job, solve_tuple)
                    # if the preprocessing did not work, abort the job and go to the next one
                    else:
                        print("\nThe pre processing was not successful, please check the control file or pre processing programs.\n")
                        return False
                    
                    # update the joblist on wheather the job was not solved in time or in loop limit
                    if not success_solving:
                        job['Status'] = "unsuccessful"
                        joblist_tuple = (joblist, full_header, value_range_list, interpreter_tuple)
                        job_management.update_joblist_files(base_name, job)                        

                    # try performing the post processing according to the success of the simulation
                    succes_post_processing = post_processing(job, base_name, success_solving, post_tuple, interpreter_tuple)
                    if succes_post_processing:
                        job['Status'] = "done"
                        joblist_tuple = (joblist, full_header, value_range_list)
                        job_management.update_joblist_files(base_name, joblist, full_header)
                        ready = True
                        continue
                    else:
                        print("\nThe post processing was not successful, check control file or post processing programs.\n")
                        return False
                
                # if anythin else goes wrong, append the job to the error list and continue the series
                except:
                    print("\nSomething went wrong.\n")
                    return False
                
    return True


control_file = "control_file.tsv"

pre_tuple = interaction.control_data_string_dict(control_file, "PRE PROCESSING")
solve_tuple = interaction.control_data_string_dict(control_file, "SIMULATION SOLVING")
post_tuple = interaction.control_data_string_dict(control_file, "POST PROCESSING")
clean_up_tuple = interaction.control_data_tuple_dict(control_file, "CLEAN UP")

design_parameter_names = pre_tuple[1]

#joblist_tuple = job_management.create_jobs("Rectangular_cup", [[1.20, 1], [1.0], [1.0], [-4.0], [0.06], [1]], design_parameter_names)


#run_simulation_series("Rectangualr_cup", joblist_tuple, pre_tuple, solve_tuple, post_tuple, clean_up_tuple)

