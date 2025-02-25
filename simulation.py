import create_jobs
import os
import time
import interaction


def pre_processing(job, editing_tuple, interpreter_tuple=None):

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
    for parameter in design_parameter_names:
        # catch the comand and job
        value = job[parameter]
        command = control_commands[parameter]
        try:

            # match the program call with the right interpreter if wished so
            if not interpreter_tuple == None:
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
                os.system(f"{interpreter} {command} {value} {jobname}")
                print(f"{interpreter} {command} {value} {jobname}")
        except:
            # if the program call did not work, something was not edited, dont continue the simulation and waste time
            success = False
            os.chdir(f"{current_working_directory}/")

    # move all generated files to the next step, next directory
    os.system(f"python move_data.py '[dat t51 t52]' {current_working_directory}/simulation_solving_programs {jobname}")
    os.chdir(f"{current_working_directory}/")
    return True

def solving_simulation(job, solve_tuple, time_limit=900, loop_limit=5):

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
    solve_data_names = solve_tuple[1]
    solve_data = solve_tuple[0]
    start_command = solve_data[solve_data_names[0]]
    done_keyword = solve_data[solve_data_names[1]]
    stop_command = solve_tuple = solve_data[solve_data_names[2]]
    jobname = job['Jobname']

    inf_file == None
    log_file == None

    # change the working directory to the one taking care of solving the simulation
    curent_working_directory = os.getcwd()
    os.chdir(f"{curent_working_directory}/simulation_solving_programs/")

    # start the simulation
    os.system(f"python {start_command} {jobname}")
    print("here alterLJBSFLJADSBFLJSKADBSADLJKFHBSADLJFFJSAJKFHB")
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

    print("here nach dem wechsel")
    # keep track of simulation 
    done = None
    loops_passed = 0
    time_passed = 0
    last_increment = None

    # check for termination constraints
    while done == None:
        time.sleep(1)

        # check wheather the simulation is done
        if check_done(jobname, done_keyword):
            done = True
        
        # check wheather the simulation exceeded its loop limit
        check_loops_result = check_loops(jobname, loop_limit, termination_keyword, loops_passed, current_length, last_length, last_increment)
        if type(check_loops_result) == tuple:
            loops_passed, current_length, last_length, last_increment = check_loops_result

        if type(check_loops_result) == bool:
            done = False    

        # check wheather the time is exceeded
        if not time_limit == None:
            if time_passed >= time_limit:
                done = False
            else:
                time_passed += 1
        print(done, loops_passed, time_passed)

    if done == False:
        os.system(f"{stop_command}")

    return done
  
def post_processing(job, post_processing_tuple):
    jobname = job['Jobname']
    post_commands, post_command_names = post_processing_tuple   

    for post_command_name in post_command_names:
        command = post_commands[post_command_name]
        os.system(f"python {command}")

def run_simulation_series(base_name, joblist_tuple, pre_tuple, solve_tuple, post_tuple, time_limit=900, loop_limit=10, interpreter_tuple=None):

    error_report_list = []

    joblist, full_header = joblist_tuple

    for job_index in range(len(joblist)):
        job = joblist[job_index]
        job['Status'] = "in progress"
        create_jobs.update_joblist_files(base_name, joblist, full_header)
        try:
            print("\n", pre_processing(job, pre_tuple, interpreter_tuple))
            print(solving_simulation(job, solve_tuple, time_limit, loop_limit))
            #print(post_processing(job, post_tuple))
        except:
            print("das hier ist passiert")
            error_report_list.append(job['Jobname'])

    if not len(error_report_list) == 0:
        with open(f"{base_name}_error_report.txt", 'a') as error_report:
            for error in error_report_list:
                error_report.write(error + "\n")

    return 


control_file = "control_file.tsv"

pre_tuple = interaction.retrieve_control_data(control_file, "PRE PROCESSING")
solve_tuple = interaction.retrieve_control_data(control_file, "SIMULATION SOLVING")
post_tuple = interaction.retrieve_control_data(control_file, "POST PROCESSING")

design_parameter_names = pre_tuple[1]
joblist_tuple = create_jobs.create_jobs("kj", [[1.0], [1.0], [1.0], [-4.0], [1.0], [1.0]], design_parameter_names)

run_simulation_series("hallo", joblist_tuple, pre_tuple, solve_tuple, post_tuple)