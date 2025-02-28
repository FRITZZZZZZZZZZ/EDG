import job_management
import simulation_management
import interaction
import sys
import create_dataset
import os

argument_vector = sys.argv

try:
    option = argument_vector[1]
    input_file_path = argument_vector[2]
except:
    pass

# Predefine dialogue lines to keep the cli dialogue readable
welcome_message = """
ENSIMA Data Generator(EDG)

For usage information see readme.md .
State 'exit' to close application at any point.

"""

index_message = """
State one of the following options as your next instruction:
-c continue
-s slave mode
-r reset control_file
-o options
exit exit 

Instruction: """

ask_reset_message = "\nAre you sure you want to reset the control_file?\n[Y/n] "

base_name_message = """
Please enter a base name for this simulation series.
This name will be associated with any result of this simulation series.

Simulation series base name: """

ask_change_message = """
State a design parameter name in order to redifine its value range or state -c to continue.
List of all available design parameter names above.

<base_name> change base name
<design_parameter_name> change parameter value range
-c continue

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


all_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

control_file_backup = r"CONTROL_FILE_BACKUP_DO_NOT_TOUCH.tsv"
control_file = "control_file.tsv"

files, file_roles = interaction.control_data_string_dict(control_file, "REQUIERED FILES")
pre_tuple = interaction.control_data_string_dict(control_file, "PRE PROCESSING")
solve_tuple = interaction.control_data_string_dict(control_file, "SIMULATION SOLVING")
post_tuple = interaction.control_data_string_dict(control_file, "POST PROCESSING")
sorting_tuple = interaction.control_data_tuple_dict(control_file, "FILE SORTING")
interpreter_tuple = interaction.control_data_string_dict(control_file, "INTERPRETER SELECTION")
csv_result_inline_keywords = interaction.control_data_direct_list(control_file, "CSV INLINE KEYWORDS")
csv_result_nextline_keywords = interaction.control_data_direct_list(control_file, "CSV NEXTLINE KEYWORDS")
csv_header = interaction.control_data_direct_list(control_file, "SIMULATION CSV HEADER")


design_parameter_names = pre_tuple[1]
design_parameter_domains = [None for parameter in design_parameter_names]

base_name = None
instruction = None
jobs_n = 1
time_limit = 900
loop_limit = 10
processing_time_limit = 5
joblist_file_exists = False
job_tuple = None

if len(argument_vector) == 1:
    print(welcome_message)

    for role in file_roles:
        try:
            current_file = files[role]
            with open(current_file, 'r') as file_current:
                pass
            file_name = files[role]
            print(f"file {role}: {file_name}\n")
        except:
            print(f"\nfile {role} could not be opened, please check working directory or change in settings.\n")

    while True:

        # first menu, user can decide to enter slave mode, reset control file, continue with series definition or exit
        while instruction == None:

            # ask wheather the user wants to reset the control file, enter slave mode, exit or continue
            index_constraint = {
                'keywords':["c", "-c", "continue", "s", "-s", "slave", "slave mode", "r", "-r", "reset", "reset control_file", "exit"],
                'allowed_characters':[],
                'unallowed_characters':[],
                'delimiters':[]
            }
            instruction = interaction.get_and_validate_input(index_message, index_constraint)

            # enter options menu
            if instruction in ["o", "-o", "options"]:
                pass

            # continue with simulation series definition
            if instruction in ["-c", "continue"]:
                instruction = None
                break

            # slave mode
            if instruction in ["s", "-s", "slave", "slave mode"]:
                interaction.slave_mode(1)
                exit()
            
            # reset control_file
            if instruction in ["r", "-r", "reset", "reset control_file"]:
                reset_confirmation_constraint = {
                    'keywords':['Y', 'n']
                }
                confirmation = interaction.get_and_validate_input(ask_reset_message, reset_confirmation_constraint)

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

                if confirmation == "n":
                    print("\nNo changes have been done to the control_file.\n")
                    instruction = None
        
        # make sure that all design parameter ranges are declared
        while None in design_parameter_domains or base_name == None:
            # ask for the base name, this is the name that every result associated with the data generation will hold
            if base_name == None:
                base_name_constraint = {'keywords':[], 'allowed_characters':all_letters + ["_"]}
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
                            if job['Status'] == "in_progess":
                                job['Status'] = "pending"
                            else:
                                pass
                        job_tuple = retrieved_job_tuple
                        
                        
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
            ask_change_constraint = {'keywords':design_parameter_names + ["c", "-c", "continue", "base name", "base_name", base_name]}
            instruction = interaction.get_and_validate_input(ask_change_message, ask_change_constraint, True)

            # declare a parameter range as None such that the loop will run again and let you redeclare its value range
            if instruction in design_parameter_names:
                for parameter_index in range(len(design_parameter_domains)):
                    if design_parameter_names[parameter_index] == instruction:
                        design_parameter_domains[parameter_index] = None
            if instruction in ["base name", base_name]:
                base_name = None
            if instruction in ["c", "-c", "continue"]:
                break
            
        # ask wheather the user wants to enter distributed mode
        distributed_mode_constraint = {
            'keywords':["Y", "n"]
        }
        instruction = interaction.get_and_validate_input(ask_distributed_message, distributed_mode_constraint)
        if instruction == "Y":
            print("multhreaded server")
            ############# TO DO MULTI DINGENS ##################
        if instruction == "n":
            pass

        # compute the number of simulations
        for value_range in design_parameter_domains:
            jobs_n *= len(value_range)

        # ask wheather the user wants to stat the simulation process
        print(f"\nIf you start the simulation series now, {jobs_n} simulation will be started.\n")
        start_constraint = {
            'keywords':["Y", "n"]
        }
        instruction = interaction.get_and_validate_input(ask_start_message, start_constraint)

        if instruction == "Y":

            if job_tuple == None:
                # create the joblist and create a joblist backup 
                job_tuple = job_management.create_jobs(base_name, design_parameter_domains, design_parameter_names)

            if not joblist_file_exists:
                # if the joblist file does not yet exist or does not contain information, it should be overwritten
                job_management.update_joblist_files(base_name, job_tuple)
            else:
                # if the joblist file is retrievable, information should only be added
                job_management.update_joblist_files(base_name, job_tuple, False)

            # simulate the jobs in the joblist and record failed simulations
            success_series = simulation_management.run_simulation_series(base_name, job_tuple, pre_tuple, solve_tuple, post_tuple, sorting_tuple, interpreter_tuple, time_limit, loop_limit, processing_time_limit)
            # if the series was successful, create the dataset
            if success_series:
                create_dataset.create_dataset(base_name, design_parameter_names, csv_result_inline_keywords, csv_result_nextline_keywords, csv_header, False)

            # ask howw the user wants to continue once the data has been generated
            ask_more_constraint = {
                'keywords':["Y", "n"]
            }
            instruction = interaction.get_and_validate_input(ask_more_message, ask_more_constraint)

            # let user exit the application 
            if instruction == "Y":
                print("\nTschüss!\n")
                exit()

            # if instruction = "n", the programm will move out of the if clause and enter the change dialogue below

        if instruction == "n":

            # ask wheather to scrap the simulation series
            ask_scrap_constraint = {
                'keywords':["Y", "n"]
            }
            instruction = interaction.get_and_validate_input(ask_scrap_message, ask_scrap_constraint)

            # scrap all value ranges and the base name
            if instruction == "n":
                base_name = None
                design_parameter_domains = [None for parameter in design_parameter_names]
                continue
            
            # do nothing
            if instruction == "Y":
                pass

            # let user change a design parameter value range
            ask_change_constraint = {
                'keywords':design_parameter_names + ["c", "-c", "continue", "base name"]
            }
            instruction = interaction.get_and_validate_input(ask_change_message, ask_change_constraint)

            # declare a parameter range as None such that the loop will run again and let you redeclare its value range
            if instruction in design_parameter_names:
                for parameter_index in range(len(design_parameter_domains)):
                    if design_parameter_names[parameter_index] == instruction:
                        design_parameter_domains[parameter_index] = None
            
            if instruction == "base name":
                base_name = None
            
            # continue on to distributed mode
            if instruction in ["c", "-c", "continue"]:
                pass

if len(argument_vector) == 3:
    if option == "-i":
        with open(input_file_path, 'r') as input_file:
            input_content = [line[:-1] for line in input_file.readlines()]

        print(input_content)
        # first input
        if input_content[0] in ["s", "-s", "slave", "slave mode"]:
            interaction.slave_mode(1)
            exit()
        
        if input_content[0] in ["-c", "continue"]:
            pass
        
        # second input
        instruction = input_content[1] 
        base_name_constraint = {
                'keywords':[],
                'allowed_characters':all_letters + ["_"]
            }
        base_name = interaction.get_and_validate_file_input(instruction, base_name_constraint)

        for parameter_index in range(len(design_parameter_names)):
            instruction = input_content[parameter_index + 2]
            design_parameter_domains[parameter_index] = interaction.get_file_design_parameter_domain(instruction)
        
        time_out = input_content[-2]

        loop_limit = input_content[-1]

        # third instruction
        joblist, full_header = job_management.create_jobs(base_name, design_parameter_domains, design_parameter_names)
        simulation_management.run_simulation_series(base_name, job, pre_tuple, post_tuple, sorting_tuple, time_out, loop_limit, interpreter_tuple)

    else:
        print("Invalid option, please restate your call!")

