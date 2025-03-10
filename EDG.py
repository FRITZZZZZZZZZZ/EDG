import job_management
import simulation_management
import interaction
import sys
import create_dataset 
import os

argument_vector = sys.argv

try:
    option = argument_vector[1]
    session_file_path = argument_vector[2]
except:
    pass

# Dialogue lines
welcome_message = """
ENSIMA Data Generator(EDG)

For usage information see readme.md .
State 'exit' to close application at any point."""
index_message = """
State one of the following options as your next instruction:
-c continue
-s slave mode
-o options

Instruction: """
option_message = """
- To alter a timer, first state the name of the timer, like so: 'simulation timer'.
Then in the next step, state the number of seconds it should last, like so: '900'.
- To alter the loop limit, first state 'loop limmit'.
Then in the next step, state the number of loops the simulation is allowed to make, like so '5'.
- To reset the control file, state '-r'.
- To exit the option menu, state '-c'.

Instruction: """
ask_reset_message = "\nAre you sure you want to reset the control_file?\n[Y/n] "
base_name_message = """
Please enter a base name for this simulation series.
This name will be associated with any result of this simulation series.
If you enter a base name that has been used before,
the related simulation series will be recovered.

Simulation series base name: """
ask_change_message = """
State a design parameter name in order to redifine its value range or state -c to continue.
State 'r' to run the simulation series again.
List of all available design parameter names above.

<base_name> change base name
<design_parameter_name> change parameter value range
-c continue
-r run the simulation series again 

<design_parameter_name> or base_name or -c: """
ask_distributed_message = """
Do you want to compute this simulation series distributedly?

You need at least one more machine with a working EDG and OpenForm installation, 
as well as a network connection.

Would you like to enter distributed mode?
[Y/n] """
ask_start_message = f"""
Do you want to start the data generation now?

This may take several houres.

Start the data generation now?
[Y/n] """
ask_scrap_message = """
Do you want to keep the predefined value ranges?

[Y/n] """
ask_more_message = """
The simulation series is done running, you can now define a new series or close this application.

Do you want to close the application?
[Y/n] """
# user statement constraint that allows for all alphabet characters
all_letters_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
all_numbers_list = ["0","1","2","3","4","5","6","7","8","9"]

# path of the control file
control_file_backup = r"CONTROL_FILE_BACKUP_DO_NOT_TOUCH.tsv"
control_file = "control_file.tsv"

# control file data
environment_tuple = interaction.control_data_string_dict(control_file, "ENVIRONMENT VARIABLES")
pre_tuple = interaction.control_data_string_dict(control_file, "PRE PROCESSING")
solve_tuple = interaction.control_data_string_dict(control_file, "SIMULATION SOLVING")
post_tuple = interaction.control_data_string_dict(control_file, "POST PROCESSING")
sorting_tuple = interaction.control_data_tuple_dict(control_file, "FILE SORTING")
interpreter_tuple = interaction.control_data_string_dict(control_file, "INTERPRETER SELECTION")
csv_result_inline_keywords = interaction.control_data_direct_list(control_file, "CSV INLINE KEYWORDS")
csv_result_nextline_keywords = interaction.control_data_direct_list(control_file, "CSV NEXTLINE KEYWORDS")
csv_header = interaction.control_data_direct_list(control_file, "SIMULATION CSV HEADER")

# simulation series related data
instruction = None
base_name = None
joblist_file_exists = False
design_parameter_names = pre_tuple[1]
design_parameter_domains = [None for parameter in design_parameter_names]
jobs_n = 1
job_tuple = None
simulation_time_limit = 900
simulation_loop_limit = 10
processing_time_limit = 5

# set up simulation solving environment
environment_variable_values, environment_variable_names = environment_tuple
for environment_variable in environment_variable_names:
    os.environ[environment_variable] = environment_variable_values[environment_variable]

# start of the conversation
print(welcome_message)
while True:
    ############################################################ index menu
    # decide between options, slave mode or continue to define a simulation series or recover a series
    while instruction == None:

        # ask wheather the user wants to reset the control file, enter slave mode, exit or continue
        index_constraint = {'keywords':["c", "-c", "continue", "s", "-s", "slave", "slave mode", "o", "-o", "options"]}
        instruction = interaction.get_and_validate_input(index_message, index_constraint)

        # continue with simulation series definition
        if instruction in ["-c", "continue"]:
            instruction = None
            break

        # slave mode
        if instruction in ["s", "-s", "slave", "slave mode"]:
            print("\nThis feature does not yet exist.\n")
            instruction = None
            #interaction.slave_mode(1)
            #exit()

        # enter options menu
        if instruction in ["o", "-o", "options"]:
            # enter a loop to stay inside the option menu
            instruction = None
            while instruction == None:
                # list the alterable elements
                print(f"\nsimulation timer: {simulation_time_limit}s\nsimulation loop limit: {simulation_loop_limit}\nprocessing timer: {processing_time_limit}s\n")
                # let user state an element he wants to alter
                option_constraint = {'keywords':["r", "-r", "reset", "reset control_file", "simulation timer", "simulation loop limit", "processing timer", "c", "-c", "continue"]}
                instruction = interaction.get_and_validate_input(option_message, option_constraint)

                # reset the simulation timer
                if instruction == "simulation timer":
                    simulation_time_limit_message = "\nSimulation time limit: "
                    integer_limit_constraint = {'allowed_characters':all_numbers_list}
                    new_simulation_time_limit = interaction.get_and_validate_input(simulation_time_limit_message, integer_limit_constraint)
                    simulation_time_limit = int(new_simulation_time_limit)
                    instruction = None

                # reset the processing timer
                if instruction == "processing timer":
                    processing_time_limit_message = "\nProcessing time limit: "
                    integer_limit_constraint = {'allowed_characters':all_numbers_list}
                    new_processing_time_limit = interaction.get_and_validate_input(processing_time_limit_message, integer_limit_constraint)
                    processing_time_limit = int(new_processing_time_limit)
                    instruction = None

                # reset the simulation loop limit
                if instruction == "simulation loop limit":
                    loop_limit_message = "\nSimulation loop limit: "
                    integer_limit_constraint = {'allowed_characters':all_numbers_list}
                    new_simulation_loop_limit = interaction.get_and_validate_input(loop_limit_message, integer_limit_constraint)
                    simulation_loop_limit = int(new_simulation_loop_limit)
                    instruction = None

                # reset the control file
                if instruction in ["r", "-r", "reset", "reset control_file"]:
                    # request a confirmation for resetting the file
                    reset_confirmation_constraint = {'keywords':['Y', 'n']}
                    confirmation = interaction.get_and_validate_input(ask_reset_message, reset_confirmation_constraint)
                    # reset the file
                    if confirmation == "Y":
                        with open(control_file, 'w') as control_file_degenerate:
                            with open(control_file_backup, 'r') as control_file_intact:
                                backup_content = control_file_intact.read()
                                control_file_degenerate.write(backup_content)
                        print("\nThe control file has been reset.\n")
                        # if the files are reset, their information must be reloaded
                        files, file_roles = interaction.control_data_string_dict(control_file, "REQUIERED FILES")
                        editing_commands, design_parameter_names = interaction.control_data_string_dict(control_file, "SIMULATION DATA")
                        action_commands, action_names = interaction.control_data_string_dict(control_file, "ACTION METHODS")
                        instruction = None
                    # continue if there is no confirmation
                    if confirmation == "n":
                        print("\nNo changes have been done to the control_file.\n")
                        instruction = None
                    
                # leave the option menu
                if instruction in ["c", "-c", "continue"]:
                    print("jetzt bin ich hier")
                    instruction = None
                    break
    
    ###################################################### define simulaiton series
    # define a simulation series or recover a series by stating a base name that already exists
    while None in design_parameter_domains or base_name == None:

        # ask for the base name, this is the name that every result associated with the data generation will hold
        if base_name == None:
            base_name_constraint = {'allowed_characters':all_letters_list + ["_"]}
            base_name = interaction.get_and_validate_input(base_name_message, base_name_constraint)

            # if the base name already exists, recover its joblist
            retrieved_job_tuple = job_management.retrieve_joblist(base_name)
            if not retrieved_job_tuple == None:
                joblist_file_exists = True
                joblist, header, value_ranges = retrieved_job_tuple
                # check wheather the header fits the design parameter names
                metaless_header = header[2:]
                if metaless_header == design_parameter_names:
                    # if the headers do match, set the design parameter value ranges to the retrieved value ranges
                    design_parameter_domains = value_ranges
                    # set all jobs that are not finished to pending
                    for job in joblist:
                        if job['Status'] == "in_progress": 
                            job['Status'] = "pending"
                        else:
                            pass
                    job_tuple = retrieved_job_tuple
                    job_management.update_joblist_files(base_name, job_tuple)
            # remember that the joblist file exists, but a retrieval did not work, it must be overwritten
            else:
                joblist_file_exists = False

        # state value ranges for each design parameter contained in the associated control_file section
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
        
        # let user change a design parameter value range
        ask_change_constraint = {'keywords':design_parameter_names + ["c", "-c", "continue", "base name", "base_name", base_name, "run again"]}
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
        if instruction == ["r", "-r"]:
            try:
                job_csv_results = os.listdir(f"raw_results/results_csv/{base_name}")
                for job in joblist:
                    jobname = job['Jobname']
                    if f"{jobname}.csv" in job_csv_results:
                        continue
                    elif job['Status'] == "unsuccessfull":
                        continue
                    else:
                        job['Status'] = "pending"
                job_tuple = (joblist, design_parameter_names, design_parameter_domains)
                job_management.update_joblist_files(base_name, job_tuple)
                break
            except:
                pass
        # continue on to distributed mode section
        if instruction in ["c", "-c", "continue"]:
            break
     
    ############################################################ distributed mode
    # ask wheather the user wants to enter distributed mode
    distributed_mode_constraint = {'keywords':["Y", "n"]}
    instruction = interaction.get_and_validate_input(ask_distributed_message, distributed_mode_constraint)

    if instruction == "Y":
        print("\nThis feature does not yet exist.\n")
        instruction = None
        pass
        ############# TO DO MULTI DINGENS ##################
    if instruction == "n":
        instruction == None
        pass

    # compute the number of simulations and ask wheather the user wants to stat the simulation process
    for value_range in design_parameter_domains:
        jobs_n *= len(value_range)
    print(f"\nIf you start the simulation series now, {jobs_n} simulation will be started.\n")
    start_constraint = {'keywords':["Y", "n"]}
    instruction = interaction.get_and_validate_input(ask_start_message, start_constraint)

    if instruction == "Y":

        # create the joblist and create a joblist backup 
        if job_tuple == None:
            job_tuple = job_management.create_jobs(base_name, design_parameter_domains, design_parameter_names)
        # if the joblist file does not yet exist or does not contain information, it should be overwritten
        if not joblist_file_exists:
            job_management.update_joblist_files(base_name, job_tuple)
        else:
            # if the joblist file is retrievable, information should only be added
            job_management.update_joblist_files(base_name, job_tuple, False)

        # simulate the jobs in the joblist and record failed simulations
        success_series = simulation_management.run_simulation_series(base_name, job_tuple, pre_tuple, solve_tuple, post_tuple, sorting_tuple, interpreter_tuple, simulation_time_limit, simulation_loop_limit, processing_time_limit)
        # if the series was successful, create the dataset
        if success_series:
            create_dataset.create_dataset(base_name, design_parameter_names, csv_result_inline_keywords, csv_result_nextline_keywords, csv_header, False)
            print(f"The data creation has been successfull, your dataset resides at complete_datasets/{base_name}.csv .")
        if not success_series:
            print("Something went wrong while running the simulation series, check the control file or editing programs.")

    # ask how the user wants to continue once the data has been generated
    ask_more_constraint = {'keywords':["Y", "n"]}
    instruction = interaction.get_and_validate_input(ask_more_message, ask_more_constraint)
    # let user exit the application 
    if instruction == "Y":
        print("\nTschüss!\n")
        exit()
    if instruction == "n":
        pass