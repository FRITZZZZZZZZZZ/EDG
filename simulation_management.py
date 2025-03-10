import job_management
import os
import time

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

def pre_processing(job, editing_tuple, interpreter_tuple, allowed_files_list):
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
            interpreter = pick_interpreter(interpreter_tuple, command)
            os.system(f"{interpreter} {command} {value} {jobname}")
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

def solving_simulation(job, solve_tuple, interpreter_tuple, time_limit, loop_limit, allowed_files_list):

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
    # the list of file types to be transfered to post processing, this is a blank space delimited list in string format
    export_file_types = solving_commands[solving_commands_names[3]]
    
    # more important variables
    jobname = job['Jobname']
    inf_file = None
    log_file = None
    allowed_files = get_allowed_files_command(allowed_files_list)

    # change the working directory to the one taking care of solving the simulation
    current_working_directory = os.getcwd()
    os.chdir(f"{current_working_directory}/simulation_solving_programs/")

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

    os.system(f"python move_data.py {export_file_types} {current_working_directory}/post_processing_programs {jobname}")

    # clean up the directory, leave only allowed files here
    os.system(f"python clean_directory.py {allowed_files}")
    os.chdir(f"{current_working_directory}/")

    return success
  
def post_processing(job, base_name, solving_success, post_tuple, file_sorting_tuple, interpreter_tuple, post_processing_time_out, allowed_files_list):
    # define important variables
    jobname = job['Jobname']
    post_commands, post_command_names = post_tuple   
    file_categories, category_names = file_sorting_tuple
    current_working_directory = os.getcwd()
    allowed_files = get_allowed_files_command(allowed_files_list)

    try:
        if solving_success:   
            

            # change the working directory to carry out work in the post processing environment
            os.chdir(f"{current_working_directory}/post_processing_programs/")
            new_working_directory = os.getcwd()

            # use the post processing programs to gather desired data and data formats from the simulation
            time_passed = 0 
            for post_command_name in post_command_names:
                command = post_commands[post_command_name]
                n_files = len(os.listdir(new_working_directory))
                # pick the right interpreter to allow use of custom programs
                interpreter = pick_interpreter(interpreter_tuple, command)
                os.system(f"{interpreter} {command} {jobname}")
                # wait for open form to export the desired file formats.                 
                while time_passed <= post_processing_time_out:
                    # This is done via time out because open form is a different process and can take some time
                    time.sleep(1)
                    time_passed += 1
                    if time_passed >= post_processing_time_out:
                        os.chdir({current_working_directory})
                        return False
                    new_n_files = len(os.listdir(new_working_directory))
                    if new_n_files > n_files:
                        break
            os.chdir(f"{current_working_directory}")

            # sort the results according to the fact that the solving has been successful
                # all categories but the last one do define data types and their destined directories for successful solving
                # the very last one is reserved for the directory that stores the files of unsuccessful solving attempts
            succes_category_names = category_names[:-1]
            for category_name in succes_category_names:
                file_types, result_path = file_categories[category_name]

                # if the directory doesnt exist, create the directory to avoid "dIrEcToRY dOEsN'T eXiST" errors
                if not os.path.isdir(f"{current_working_directory}/{result_path}/{base_name}/"):
                    os.mkdir(f"{current_working_directory}/{result_path}/{base_name}/")

                # move the files to their destination folder
                os.chdir(f"{current_working_directory}/post_processing_programs")
                os.system(f"python move_data.py {file_types} {current_working_directory}/{result_path}/{base_name} {jobname}")
                os.chdir(f"{current_working_directory}")

        if not solving_success:

            # only the last category_name deals with files of unsuccessful solving attempts
            error_category = category_names[-1]
            file_types, result_path = file_categories[error_category]

            # if the directory doesnt exist, create the directory to avoid "dIrEcToRY dOEsN'T eXiST" errors
            if not os.path.isdir(f"{current_working_directory}/{result_path}/{base_name}/"):
                os.mkdir(f"{current_working_directory}/{result_path}/{base_name}/")

            # move the files to the folder storing the data of unsuccessful solving atttempts
            os.chdir(f"{current_working_directory}/post_processing_programs")
            os.system(f"python move_data.py {file_types} {current_working_directory}/{result_path}/{base_name} {jobname}")
            os.chdir(f"{current_working_directory}")

    except:
        # clean up the directory, leave only allowed files here
        os.chdir(f"{current_working_directory}/post_processing_programs")
        os.system(f"python clean_directory.py {allowed_files}")
        os.chdir(f"{current_working_directory}")
        return False

    # clean up the directory, leave only allowed files here
    os.chdir(f"{current_working_directory}/post_processing_programs")
    os.system(f"python clean_directory.py {allowed_files}")
    os.chdir(f"{current_working_directory}")
    return True

def run_simulation_series(base_name, joblist_tuple, pre_tuple, solve_tuple, post_tuple, sorting_tuple, interpreter_tuple=None, time_limit=900, loop_limit=10, processing_time_limit=60 ):

    # defining important control variables
    joblist, full_header, value_range_list = joblist_tuple
    ready = True

    # catch the directory states such that its clear which files are allowed in the directories, all other files will be deleted
    current_working_directory = os.getcwd()
    pre_processing_files = os.listdir(f"{current_working_directory}/pre_processing_programs")
    simulation_solving_files = os.listdir(f"{current_working_directory}/simulation_solving_programs")
    post_processing_files = os.listdir(f"{current_working_directory}/post_processing_programs")

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
                job_management.update_joblist_files(base_name, joblist_tuple)

                # try solving the job
                try:
                    # start the preprocessing and prepare the input data
                    success_pre_processing = pre_processing(job, pre_tuple, interpreter_tuple, pre_processing_files)
                    # start the simulation once the preprocessing was succcsessful, append to error list else
                    if success_pre_processing:
                        success_solving = solving_simulation(job, solve_tuple, interpreter_tuple, time_limit, loop_limit, simulation_solving_files)
                    # if the preprocessing did not work, abort the job and go to the next one
                    else:
                        print("\nThe pre processing was not successful, please check the control file or pre processing programs.\n")
                        return False
                    # update the joblist on wheather the job was not solved in time or in loop limit
                    if not success_solving:
                        job['Status'] = "unsuccessfull"
                        joblist_tuple = (joblist, full_header, value_range_list)
                        job_management.update_joblist_files(base_name, joblist_tuple)                                   

                    # try performing the post processing according to the success of the simulation
                    succes_post_processing = post_processing(job, base_name, success_solving, post_tuple, sorting_tuple, interpreter_tuple, processing_time_limit, post_processing_files)
                    if succes_post_processing:
                        job['Status'] = "successfull"
                        joblist_tuple = (joblist, full_header, value_range_list)
                        job_management.update_joblist_files(base_name, joblist_tuple)
                        ready = True
                        continue
                    else:
                        print("\nThe post processing was not successful, check control file or post processing programs.\n")
                        return False
                # if anythin else goes wrong, append the job to the error list and continue the series
                except:
                    print("\nSomething went wrong while running the simulation series.\n")
                    return False
                
    return True

#post_processing({'Jobname': 'sdfg_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_1.0_ScX_1.0_ScY_1.0', 'Status': 'unsuccessful', 'Blank Thickness': 1.0, 'Binder Friction': 1.0, 'Binder Pressure': -4.0, 'Die Radius': 1.0, 'Scale X': 1.0, 'Scale Y': 1.0}, "sdfg", False, ({'Export Screenshot': 'export_png.py', 'Export CSV': 'export_csv.py'}, ['Export Screenshot', 'Export CSV']), ({'Result Raw Folders': ('erg', 'raw_results/erg_folders'), 'Result Png': ('png', 'raw_results/results_png'), 'Result CSV': ('csv', 'raw_results/results_csv'), 'Error Files': ("'inf log out'", 'raw_results/error_results')}, ['Result Raw Folders', 'Result Png', 'Result CSV', 'Error Files']), None, 10, ['move_data.py', 'clean_directory.py', 'SessionFileShowAndExportPost.ofs', 'export_csv.py', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.log', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.t51', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.inf', 'export_png.py', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.erg', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.t52', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.dat', 'dsfjkh_BlTh_1.0_BiFr_1.0_BiPr_-4.0_DiRa_3.0_ScX_1.0_ScY_1.0.out'])