import job_management
import simulation_management
import interaction
import sys
import create_dataset 
import os
import session_file_management
import multithreaded_server

def options(instruction):
    option_message = """
    - To alter a timer, first state the name of the timer, like so: 'simulation_time_limit'.
    Then in the next step, state the number of seconds it should last, like so: '900'.
    - To alter the loop limit, first state 'simulation_loop_limit'.
    Then in the next step, state the number of loops the simulation is allowed to make, like so '5'.
    - To append a header to the finished dataset, state 'dataset_header'.
    - To reset the control file, state '-r'.
    - To exit the option menu, state '-c'.

    Instruction: """
    ask_reset_message = """
    Do you really want to reset the control file?
    
    [Y/n] """
    while instruction == None:
        # list the alterable elements
        with open(option_file_path, 'r') as option_file:
            option_content = [line for line in option_file.readlines()]
            print("\n")
            for line in option_content:
                print(line[:-1])
        # let user state an element he wants to alter
        option_constraint = {'keywords':["r", "-r", "reset", "reset control file", "simulation_time_limit", "simulation_loop_limit", "processing_time_limit", "c", "-c", "continue", "dataset header"]}
        instruction = interaction.get_and_validate_input(option_message, option_constraint)

        # reset the simulation timer
        if instruction == "simulation_time_limit":
            simulation_time_limit_message = "\nSimulation time limit: "
            integer_limit_constraint = {'allowed_characters':all_numbers_list}
            new_simulation_time_limit = interaction.get_and_validate_input(simulation_time_limit_message, integer_limit_constraint)
            simulation_time_limit = int(new_simulation_time_limit)
            interaction.read_write_options(option_file_path, "simulation_time_limit", simulation_time_limit)
            instruction = None

        # reset the processing timer
        if instruction == "processing_time_limit":
            processing_time_limit_message = "\nProcessing time limit: "
            integer_limit_constraint = {'allowed_characters':all_numbers_list}
            new_processing_time_limit = interaction.get_and_validate_input(processing_time_limit_message, integer_limit_constraint)
            processing_time_limit = int(new_processing_time_limit)
            interaction.read_write_options(option_file_path, "processing_time_limit", processing_time_limit)
            instruction = None

        # reset the simulation loop limit
        if instruction == "simulation_loop_limit":
            loop_limit_message = "\nSimulation loop limit: "
            integer_limit_constraint = {'allowed_characters':all_numbers_list}
            new_simulation_loop_limit = interaction.get_and_validate_input(loop_limit_message, integer_limit_constraint)
            simulation_loop_limit = int(new_simulation_loop_limit)
            interaction.read_write_options(option_file_path, "simulation_loop_limit", simulation_loop_limit)
            instruction = None

        # choose wheather to append a header to the datasset
        if instruction == "dataset_header":
            dataset_header_message = "\nAppend a dataset header?\n[Y/n] "
            dataset_header_constraint = {'keywords':['Y', 'n']}
            new_dataset_header = interaction.get_and_validate_input(dataset_header_message, dataset_header_constraint)
            if new_dataset_header == "Y":
                dataset_header = True
                interaction.read_write_options(option_file_path, "dataset_header", "True")
            if new_dataset_header == "n":
                dataset_header = False
                interaction.read_write_options(option_file_path, "dataset_header", "False")
            instruction = None

        # reset the control file
        if instruction in ["r", "-r", "reset", "reset control file"]:
            # request a confirmation for resetting the file
            reset_confirmation_constraint = {'keywords':['Y', 'n']}
            confirmation = interaction.get_and_validate_input(ask_reset_message, reset_confirmation_constraint)
            # reset the file
            if confirmation == "Y":
                with open(control_file_path, 'w') as control_file_degenerate:
                    with open(control_file_backup_path, 'r') as control_file_intact:
                        backup_content = control_file_intact.read()
                        control_file_degenerate.write(backup_content)
                print("\nThe control file has been reset.\n")
                # if the files are reset, their information must be reloaded
                environment_tuple = interaction.control_data_string_dict(control_file_path, "ENVIRONMENT VARIABLES")
                pre_tuple = interaction.control_data_string_dict(control_file_path, "PRE PROCESSING")
                solve_tuple = interaction.control_data_string_dict(control_file_path, "SIMULATION SOLVING")
                csv_result_inline_keywords = interaction.control_data_direct_list(control_file_path, "CSV INLINE KEYWORDS")
                csv_result_nextline_keywords = interaction.control_data_direct_list(control_file_path, "CSV NEXTLINE KEYWORDS")
                csv_header = interaction.control_data_direct_list(control_file_path, "SIMULATION CSV HEADER")
                # reset the instruction to none
                instruction = None
            # continue if there is no confirmation
            if confirmation == "n":
                print("\nNo changes have been done to the control file.\n")
                instruction = None
            
        # leave the option menu
        if instruction in ["c", "-c", "continue"]:
            instruction = None
            break
    return instruction

def index_menu(instruction):
    index_message = """
    State one of the following options as your next instruction:
    -c continue
    -s slave mode
    -o options

    Instruction: """
    while not instruction in ["c", "-c", "continue"] and not session_file_exists:
        # if the session file defines a command for this step, use the command

        # ask wheather the user wants to reset the control file, enter slave mode, exit or continue
        index_constraint = {'keywords':["c", "-c", "continue", "s", "-s", "slave", "slave mode", "o", "-o", "option", "options"]}
        instruction = interaction.get_and_validate_input(index_message, index_constraint)

        # continue with simulation series definition
        if instruction in ["-c", "continue"]:
            instruction = None
            break

        # enter slave mode
        if instruction in ["s", "-s", "slave", "slave mode"]:
            # backup all pre_processing_programs
            self_pre_processing_programs = os.listdir("pre_processing_programs")
            for file in self_pre_processing_programs:
                with open(file, 'rb') as self_file:
                    with open(f"backup_{file}", 'wb') as backup_file:
                        backup_file.write(self_file.read())
            # enter slave mode
                
            #interaction.slave_mode(1)
            # rollback any changes the master did to the slave machine
            for file in self_pre_processing_programs:
                with open(f"backup_{file}", 'rb') as backup_file:
                    with open(file, 'wb') as self_file:
                        self_file.write(backup_file.read())
                os.remove(f"backup_{file}")
            exit()

        # enter options menu
        if instruction in ["o", "-o", "option","options"]:
            # enter a loop to stay inside the option menu
            instruction = None
            instruction = options(instruction)
    return instruction

def define_or_post_series(design_parameter_domains, base_name, instruction):
    base_name_message = """
    Please enter a base name for this simulation series.
    This name will be associated with any result of this simulation series.
    If you enter a base name that has been used before,
    the related simulation series will be recovered.

    Simulation series base name: """
    ask_change_message = """
    State a design parameter name in order to redifine its value range.
    State 'base name' in order to change the base name.
    List of all available design parameter names above.

    -'base name' to change base name
    <design_parameter_name> change parameter value range
    -c continue
    -r reset the Simulation Series to run failes jobs again
    -p run the post processing for this joblist
    -o options

    Instruction: """
    ask_png_message = """
    Do you want to export an image of the result structure with every csv?

    Additional space is requiered.

    [Y/n] """
    # define a simulation series or recover a series by stating a base name that already exists
    while None in design_parameter_domains or base_name == None or instruction == None:

        # try to catch the base name from the session file
        if session_file_exists:
            if not command_list[2] == None:
                base_name = command_list[2]

        # ask for the base name, this is the name that every result associated with the data generation will hold
        if base_name == None:
            base_name_constraint = {'allowed_characters':all_letters_list + ["_"]}
            base_name = interaction.get_and_validate_input(base_name_message, base_name_constraint)
            # if the base name already exists, recover its joblist
            retrieved_job_tuple = job_management.retrieve_joblist(base_name)
            if not retrieved_job_tuple == None:
                joblist_file_exists = True
                joblist, header, value_ranges = retrieved_job_tuple
                jobs_done = [jobname[:-4] for jobname in os.listdir(f"raw_results/erg_folders/{base_name}")]
                # check wheather the header fits the design parameter names
                metaless_header = header[2:]
                if metaless_header == design_parameter_names:
                    design_parameter_domains = value_ranges
                    # set all jobs that are not finished to pending
                    for job in joblist:
                        if job['Status'] == "in_progress": 
                            job['Status'] = "pending"
                        if job['Jobname'] in jobs_done:
                            job['Status'] = "successfull"
                    job_tuple = retrieved_job_tuple
                    job_management.update_joblist_files(base_name, job_tuple)
            # remember that the joblist file exists, but a retrieval did not work, it must be overwritten
            else:
                joblist_file_exists = False

        # try to catch the parameter domains from the session file
        if session_file_exists:
            if not command_list[3] == None:
                if len(command_list[3]) == len(design_parameter_names):
                    design_parameter_domains = command_list[3]
                    instruction = "-c"
                    continue
            if joblist_file_exists:
                instruction = "-c"
                continue
            else:
                pass

        # state value ranges for each design parameter contained in the associated control file section
        if None in design_parameter_domains:
            for parameter_index in range(len(design_parameter_names)):
                parameter_name = design_parameter_names[parameter_index]
                if design_parameter_domains[parameter_index] == None:
                    new_domain = interaction.request_design_parameter_domain(parameter_name)
                    design_parameter_domains[parameter_index] = new_domain
        # give user a summery of the simulation series
        print("\nIf you want to change a value range, just state the design Parameter name.\n Available names:\n")
        for parameter_index in range(len(design_parameter_names)):
            parameter_name = design_parameter_names[parameter_index]
            parameter_domain = design_parameter_domains[parameter_index]
            print(f"{parameter_name}\n{parameter_domain}\nnumber of values: {len(parameter_domain)}\n")
        
        # let user change a design parameter value range, base name or timer
        ask_change_constraint = {'keywords':design_parameter_names + ["c", "-c", "continue", "base name", "base_name", base_name, "r", "-r", "p", "-p", "-post", "post", "o", "-o", "options"]}
        instruction = interaction.get_and_validate_input(ask_change_message, ask_change_constraint, True)
        # declare a parameter range as None such that the loop will run again and let you redeclare its value range
        if instruction in design_parameter_names:
            for parameter_index in range(len(design_parameter_domains)):
                if design_parameter_names[parameter_index] == instruction:
                    design_parameter_domains[parameter_index] = None
        # reset the base name
        if instruction in ["base name", base_name]:
            base_name = None
        # reset the joblist in order to re run the simulation series
        if instruction in ["r", "-r"]:
            try:
                job_csv_results = os.listdir(f"raw_results/results_csv/{base_name}")
                for job in joblist:
                    jobname = job['Jobname']
                    if f"{jobname}.csv" in job_csv_results:
                        continue
                    else:
                        job['Status'] = "pending"
                job_tuple = (joblist, full_header, design_parameter_domains)
                job_management.update_joblist_files(base_name, job_tuple)
                print("\nThe joblist has been reset, all unsuccessfull jobs can be Simulated again.\n")
            except:
                pass
            instruction = None

        # perform the post processing
        if instruction in ["p", "-p", "-post", "post"]:
            
            # ask wheather a png should be exported too, then export all csv files and png if wished so
            png_constraint = {'keywords':["Y", "n"]}
            instruction = interaction.get_and_validate_input(ask_png_message, png_constraint)

            if instruction == "Y":
                create_dataset.export_data(base_name, True)
            
            if instruction == "n":
                create_dataset.export_data(base_name)
           
        # give user access to all options
        if instruction in ["o", "-o", "option", "options"]:
            # enter a loop to stay inside the option menu
            instruction = None
            instruction = options(instruction)
            
        # continue on to distributed mode section
        if instruction in ["c", "-c", "continue"]:
            instruction = None
            break

    return design_parameter_domains

def distributed_mode(base_name, design_parameter_domains, design_parameter_names, joblist_file_exists):
    ask_distributed_message = """
    Do you want to compute this simulation series distributedly?

    You need at least one more machine with a working EDG and OpenForm installation, 
    as well as a network connection.

    Would you like to enter distributed mode?
    [Y/n] """
    distributed_mode_constraint = {'keywords':["Y", "n"]}
    instruction = interaction.get_and_validate_input(ask_distributed_message, distributed_mode_constraint)

    if session_file_exists:
        if command_list[4] == None:
            instruction = "n"
        else:
            instruction = "Y"
    
    # enter the distributed mode
    if instruction == "Y":
        # create the job tuple if it does not exist, update the joblist accordingly
        if job_tuple == None:
            job_tuple = job_management.create_jobs(base_name, design_parameter_domains, design_parameter_names)
        job_management.update_joblist_files(base_name, job_tuple, (not joblist_file_exists))
        multithreaded_server.multithread_server(job_tuple)
            

def central_only(jobs_n, design_parameter_domains, design_parameter_names, job_tuple):   
    ask_start_message = f"""
    Do you want to start the data generation now?

    This may take several houres.

    Start the data generation now?
    [Y/n] """
    # stay in centralized mode
    instruction = None
    # compute the number of simulations and ask wheather the user wants to stat the simulation process
    for value_range in design_parameter_domains:
        jobs_n *= len(value_range)
    print(f"\nIf you start the simulation series now, {jobs_n} simulation will be started.\n")
    start_constraint = {'keywords':["Y", "n"]}
    instruction = interaction.get_and_validate_input(ask_start_message, start_constraint)

    if session_file_exists:
        if command_list[4] == None:
            instruction = "Y"

    # create the job tuple if it does not exist, update the joblist accordingly 
    if instruction == "Y":
        if job_tuple == None:
            job_tuple = job_management.create_jobs(base_name, design_parameter_domains, design_parameter_names)
        job_management.update_joblist_files(base_name, job_tuple, (not joblist_file_exists))
        success_series = simulation_management.run_simulation_series(base_name, job_tuple, pre_tuple, solve_tuple, simulation_time_limit, simulation_loop_limit, processing_time_limit)
        
    # if the series was successful, create the dataset
    if success_series:
        create_dataset.create_dataset(base_name, design_parameter_names, csv_result_inline_keywords, csv_result_nextline_keywords, csv_header, dataset_header)
        print(f"The data creation has been successfull, your dataset resides at complete_datasets/{base_name}.csv .")
    if not success_series:
        print("Something went wrong while running the simulation series, check the control file or editing programs.")

######################################################## RETRIVAL OF DATA AND VARIABLE INITIALISATION ##################################################

# user statement constraint that allows for all alphabet characters
all_letters_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
all_numbers_list = ["0","1","2","3","4","5","6","7","8","9"]

# paths of persistent files
current_working_directory = os.getcwd()
control_file_backup_path = f"{current_working_directory}/persistent_memory/CONTROL_FILE_BACKUP_DO_NOT_TOUCH.tsv"
control_file_path = f"control_file.tsv"
option_file_path = f"{current_working_directory}/persistent_memory/EDG_options.txt"
session_file_backup_path = f"{current_working_directory}/persistent_memory/EDG_session_file_BACKUP_DO_NOT_TOUCH.txt"

# control file data
environment_tuple = interaction.control_data_string_dict(control_file_path, "ENVIRONMENT VARIABLES")
pre_tuple = interaction.control_data_string_dict(control_file_path, "PRE PROCESSING")
solve_tuple = interaction.control_data_string_dict(control_file_path, "SIMULATION SOLVING")
csv_result_inline_keywords = interaction.control_data_direct_list(control_file_path, "CSV INLINE KEYWORDS")
csv_result_nextline_keywords = interaction.control_data_direct_list(control_file_path, "CSV NEXTLINE KEYWORDS")
csv_header = interaction.control_data_direct_list(control_file_path, "SIMULATION CSV HEADER")

# simulation series related data
session_file_exists = False
instruction = None
base_name = None
joblist_file_exists = False
design_parameter_names = pre_tuple[1]
full_header = ['Jobname', 'Status'] + design_parameter_names
design_parameter_domains = [None for parameter in design_parameter_names]
job_tuple = None
jobs_n = 1
simulation_time_limit = int(interaction.read_write_options(option_file_path, "simulation_time_limit"))
simulation_loop_limit = int(interaction.read_write_options(option_file_path, "simulation_loop_limit"))
processing_time_limit = int(interaction.read_write_options(option_file_path, "processing_time_limit"))
dataset_header = interaction.read_write_options(option_file_path, "dataset_header")

# create a blank session file corresponding to the job and look for a session file in the argument vector
session_file_management.write_blank_session_file(design_parameter_names, session_file_backup_path)
session_file_path = None
argument_vector = sys.argv
try:
    session_file_path = argument_vector[1]
except:
    pass
if not session_file_path == None:
    session_file_exists = True
    command_list = session_file_management.read_session_file(session_file_path)
    simulation_time_limit = command_list[0]
    simulation_loop_limit = command_list[1]

# set up simulation solving environment
environment_variable_values, environment_variable_names = environment_tuple
for environment_variable in environment_variable_names:
    os.environ[environment_variable] = environment_variable_values[environment_variable]

print("""
ENSIMA Data Generator(EDG)

For usage information see readme.md .
State 'exit' to close application at any point.""")

##################################################### THE USER DIALOGUE STARTS HERE ##################################################################

while True:
    index_menu(instruction)
    design_parameter_domains = define_or_post_series(design_parameter_domains, base_name, instruction)
    distributed_mode(base_name, design_parameter_domains, design_parameter_names, joblist_file_exists)
    central_only(jobs_n, design_parameter_domains, design_parameter_names, job_tuple)