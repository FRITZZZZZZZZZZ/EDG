import job_management
import os
import time
import random

def pick_interpreter(interpreter_tuple, command=None):
    """"
    This program takes a command and matched it to the right interpreter, it a interpreter list is passed.
    """
    if not interpreter_tuple == None and not command == None:
        interpreters, language_suffixes = interpreter_tuple
        program_call = command.split(' ')[0]
        file_suffix = program_call.split('.')[1]
        for suffix in language_suffixes:
            if suffix == file_suffix:
                interpreter = interpreters[suffix]
                return interpreter
            else:
                # if the suffix is unknown try running the program as is
                interpreter = ''
    else:
        interpreter = "python"
        return interpreter

def get_allowed_files_command(allowed_files):
    allowed_files_command = ""
    for file in allowed_files:
        allowed_files_command += file + " "
    allowed_files_command = "'" + allowed_files_command[:-1] + "'"
    return allowed_files_command

def pre_processing(job, editing_tuple, allowed_files_list):
    """
    This function takes care of the pre processing of the simulation. It alters input files like dat t51 and t52
    and then moves them to the next step.
    """
    # unpack control data tuples
    control_commands, design_parameter_names = editing_tuple
    allowed_files = get_allowed_files_command(allowed_files_list)
    jobname = job["Jobname"]

    # remember the current working directory
    current_working_directory = os.getcwd()

    # change the current working directory to the one housing the pre processing methods
    success = None

    # prepare simulation by editing job data for every design parameter
    os.chdir(f"{current_working_directory}/pre_processing_programs/")

    for parameter in design_parameter_names:

        # catch the comand and job
        value = job[parameter]
        command = control_commands[parameter]
        try:
            # match the program call with the right interpreter if wished so
            os.system(f"{command} {value} {jobname}")
        except:
            # if the program call did not work, something was not edited, dont continue the simulation and waste time
            os.system(f"python clean_directory.py {allowed_files}")
            os.chdir(f"{current_working_directory}/")
            success = False
            return success

    # if the pre processing was successful, the files will be transfered to the next step
    os.system(f"python move_data.py 'dat t51 t52' {current_working_directory}/simulation_solving_programs {jobname}")

    # clean up the directory, leave only allowed files here
    os.system(f"python clean_directory.py {allowed_files}")

    os.chdir(f"{current_working_directory}/")
    success = True
    return success

def solve_simulation(job, base_name, solve_tuple, time_limit, loop_limit, allowed_files_list):

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
    start_command = solving_commands[solving_commands_names[0]]
    done_keyword = solving_commands[solving_commands_names[1]]
    
    # more important variables
    jobname = job['Jobname']
    inf_file = None
    log_file = None
    allowed_files = get_allowed_files_command(allowed_files_list)

    # change the working directory to the one taking care of solving the simulation
    current_working_directory = os.getcwd()
    os.chdir(f"{current_working_directory}/simulation_solving_programs/")

    # start the simulation
    os.system(f"{start_command} {jobname}")

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

    # keep track of simulation and check for termination constraints
    success = None
    loops_passed = 0
    time_passed = 0
    last_increment = None
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

    if success:
        if not os.path.isdir(f"{current_working_directory}/raw_results/erg_folders/{jobname}"):
            os.mkdir(f"{current_working_directory}/raw_results/erg_folders/{jobname}")
        os.system(f"python move_data.py erg {current_working_directory}/raw_results/erg_folders/{jobname} {jobname}")
    if not success:
        if not os.path.isdir(f"{current_working_directory}/raw_results/error_results/{base_name}/{jobname}"):
            os.mkdir(f"{current_working_directory}/raw_results/error_results/{base_name}/{jobname}")
        os.system(f"python move_data.py 'erg t51 t52 inf log out dat' {current_working_directory}/raw_results/error_results/{base_name}{jobname} {jobname}")

    # clean up the directory, leave only allowed files here
    os.system(f"python clean_directory.py {allowed_files}")
    os.chdir(f"{current_working_directory}/")

    return success
  

def run_simulation_series(base_name, joblist_tuple, pre_tuple, solve_tuple, time_limit=900, loop_limit=10, processing_time_limit=60 ):

    # defining important control variables
    joblist, full_header, value_range_list = joblist_tuple
    ready = True

    # catch the directory states such that its clear which files are allowed in the directories, all other files will be deleted
    current_working_directory = os.getcwd()
    pre_processing_files = os.listdir(f"{current_working_directory}/pre_processing_programs")
    simulation_solving_files = os.listdir(f"{current_working_directory}/simulation_solving_programs")

    for job_index in range(len(joblist)):
        if ready:
            ready = False
            job = joblist[job_index]
            
            if not job['Status'] == 'pending':
                ready = True
                continue

            else:
                job['Status'] = "in_progress"
                joblist_tuple = (joblist, full_header, value_range_list)
                job_management.update_joblist_files(base_name, joblist_tuple)

                # try solving the job
                try:
                    #if the preprocessing did not work, abort the job and go to the next one
                    success_pre_processing = pre_processing(job, pre_tuple, pre_processing_files)
                    if not success_pre_processing:
                        print("\nThe pre processing was not successful, please check the control file or pre processing programs.\n")
                        return False
                    
                    # if the solving was not successfull, the success of the post processing is not important
                    success_solving = solve_simulation(job, base_name, solve_tuple, time_limit, loop_limit, simulation_solving_files)
                    
                    # label the job in the joblist
                    if success_solving:
                        job['Status'] = "successfull"
                    else:
                        job['Status'] = "unsuccessfull"
                    joblist_tuple = (joblist, full_header, value_range_list)
                    job_management.update_joblist_files(base_name, joblist_tuple)                                

                    ready = True
                    
                except:
                    print("\nSomething went wrong while running the simulation series.\n")
                    return False
    return True



def simulate(job):
    print(job)
    time_dings = random.randint(3, 10)
    print("done")
