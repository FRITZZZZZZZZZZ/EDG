import os

current_working_directory = os.getcwd()
os.chdir(f"{current_working_directory}/pre_processing_programs/")
os.system("python move_data.py '[1 2 3 4 5]'")
print("jetzt hier", os.getcwd())
os.chdir(f"{current_working_directory}")
print("jetzt hier", os.getcwd())

def simulate(job, editing_tuple, action_tuple, termination_tuple, time_limit=900, loop_limit=5, interpreter_tuple=None):

    # unpack control data tuples
    control_commands, design_parameter_names = editing_tuple
    action_commands, action_names = action_tuple
    termination_keywords, termination_keyword_names = termination_tuple

    if not interpreter_tuple == None:
        interpreters, interpreter_suffixes = interpreter_tuple

    inf_file = None
    log_file = None
    
    termination_keyword_name = termination_keyword_names[0]
    termination_keyword = termination_keywords[termination_keyword_name]

    jobname = job["Jobname"]

    # prepare simulation by editing job data for every design parameter
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
            print(f"{interpreter} {command} {value} {jobname}")
            os.system(f"{interpreter} {command} {value} {jobname}")
        except:

            # if the program call did not work, something was not edited, dont continue the simulation and waste time
            return False

    start_command_name = action_names[0]
    start_command = action_commands[start_command_name]
    os.system(f"python {start_command} {jobname}")

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

    # create control threats if wished so
    done = None

    loops_passed = 0
    time_passed = 0
    last_increment = None

    # check for termination constraints
    while done == None:
        time.sleep(1)

        # check wheather the simulation is done
        if check_done(jobname, " Ende  der Berechnung am"):
            done = True
        
        # check wheather the simulation exceeded its loop limit
        check_loops_result = check_loops(jobname, loop_limit, termination_keyword, loops_passed, current_length, last_length, last_increment)
        if type(check_loops_result) == tuple:
            loops_passed, current_length, last_length, last_increment = check_loops_result
            #print(loops_passed, current_length, last_length, last_increment, "das sind die results")
        if type(check_loops_result) == bool:
            done = False    

        # check wheather the time is exceeded
        if not time_limit == None:
            if time_passed >= time_limit:
                done = False
            else:
                time_passed += 1

        print(done, time_passed, loops_passed, check_done(jobname, " Ende  der Berechnung am"))
            
    if done:

        for action_name in action_names[1:]:
            action_command = action_commands[action_name]

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
            os.system(f"{interpreter} {action_command}")
        return True

    if not done:
        os.system("SIGNAL STOP")
        return False

def simulate_compact(base_name, full_header, job, editing_tuple, action_tuple, termination_tuple, time_out, loop_limit, interpreter_tuple):
    success = simulate(job, editing_tuple, action_tuple, termination_tuple, time_out, loop_limit, interpreter_tuple)
    if success:
        job["Status"] = "done"
        create_jobs.update_joblist_files(base_name, joblist, full_header)
    else:
        job["Status"] = "unsuccessfull"
        create_jobs.update_joblist_files(base_name, joblist, full_header)