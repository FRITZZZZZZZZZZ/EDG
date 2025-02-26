import socket
import time

"""
This module implements Methods that allow EDG to interact with different entities such as humans, secondary storage or other machines.
"""


########## machine / human interaction ##########



def validate_input(user_input, input_constraints):
    """
    This function lets you filter out invalid user inputs.

    - You dont have to use all constraint types but make sure to 
    name the constraint types correctly when declaring the constraint
    dictionary in your program.
    - If you dont define anything, nothing will be filtered out.
    - Inputs containing predefined keywords will pass right through.
    - Inputs containing anything else than allowed_characters will need to be restated.
    - Inputs containing unallowed_characters will need to be restated.
    - Inputs containing more than one exlusive_delimiters need to be restated.
    
    This function will not avoid all errornous user inputs but narrows their range
    down dramaticly.
    
    Catch further invalid user inputs during the input processing function execution.
    
    Use this function whenever user input is needed, to document the nature of the input.
    """

    # predefine all variables needed for execution, will be ignored when it is empty list
    keywords = []
    allowed_characters = []
    disallowed_characters = []
    delimiters = []

    # catch the constrained dictionary, works with full or partial definition
    try:
        keywords = input_constraints['keywords']
        allowed_characters = input_constraints['allowed_characters']
        disallowed_characters = input_constraints['disallowed_characters']
        delimiters = input_constraints['exclusive_delimiters']
    except:
        pass

    # catch the users wish to exit
    if user_input == "exit":
        exit()

    # let keywords pass through
    if user_input in keywords:
        return True

    # if allowed characters are defined, stop anything that uses characters other than allowed ones
    if len(allowed_characters)>0:
        for user_character in user_input:
            if user_character in allowed_characters:
                continue
            else: 
                print("\nInvalid input, please restate your instruction.")
                return False
    
    # if disallowed characters are defined, stop anything that uses one of them
    if len(disallowed_characters)>0:        
        for user_character in user_input:
            if user_character in disallowed_characters:
                print("\nInvalid input, please restate your instruction.")
                return False

    # if there are two exclusive delimiters present at the same time, stop the input
    if len(delimiters)>0:
        both_delimiters_contained = True
        for delimiter in delimiters:
            both_delimiters_contained = both_delimiters_contained and delimiter in user_input
        if both_delimiters_contained:
            print("\nInvalid input, only use one delimitter.")
            return False
        
    # if inputs are stopped based on black or white listing, allow anything that has not been stopped
    # this enables the user to define unique names. Else, stop anything that has not been passed through
    if len(allowed_characters)>0 or len(disallowed_characters)>0:
        return True
    else:
        print("\nInvalid input, please restate your instruction.\n")
        return False
    

def validate_input(user_input, input_constraints):
    """
    This function lets you filter out invalid user inputs.

    - You dont have to use all constraint types but make sure to 
    name the constraint types correctly when declaring the constraint
    dictionary in your program.
    - If you dont define anything, nothing will be filtered out.
    - Inputs containing predefined keywords will pass right through.
    - Inputs containing anything else than allowed_characters will need to be restated.
    - Inputs containing unallowed_characters will need to be restated.
    - Inputs containing more than one exlusive_delimiters need to be restated.
    
    This function will not avoid all errornous user inputs but narrows their range
    down dramaticly.
    
    Catch further invalid user inputs during the input processing function execution.
    
    Use this function whenever user input is needed, to document the nature of the input.
    """

    # predefine all variables needed for execution, will be ignored when it is empty list
    keywords = []
    allowed_characters = []
    disallowed_characters = []
    delimiters = []

    # catch the constrained dictionary, works with full or partial definition
    try:
        keywords = input_constraints['keywords']
        allowed_characters = input_constraints['allowed_characters']
        disallowed_characters = input_constraints['disallowed_characters']
        delimiters = input_constraints['exclusive_delimiters']
    except:
        pass

    # catch the users wish to exit
    if user_input == "exit":
        exit()

    # let keywords pass through
    if user_input in keywords:
        return True

    # if allowed characters are defined, stop anything that uses characters other than allowed ones
    if len(allowed_characters)>0:
        for user_character in user_input:
            if user_character in allowed_characters:
                continue
            else: 
                print("\nInvalid input, please restate your instruction.")
                return False
    
    # if disallowed characters are defined, stop anything that uses one of them
    if len(disallowed_characters)>0:        
        for user_character in user_input:
            if user_character in disallowed_characters:
                print("\nInvalid input, please restate your instruction.")
                return False

    # if there are two exclusive delimiters present at the same time, stop the input
    if len(delimiters)>0:
        both_delimiters_contained = True
        for delimiter in delimiters:
            both_delimiters_contained = both_delimiters_contained and delimiter in user_input
        if both_delimiters_contained:
            print("\nInvalid input, only use one delimitter.")
            return False
        
    # if inputs are stopped based on black or white listing, allow anything that has not been stopped
    # this enables the user to define unique names. Else, stop anything that has not been passed through
    if len(allowed_characters)>0 or len(disallowed_characters)>0:
        return True
    else:
        print("\nInvalid input, please restate your instruction.\n")
        return False
        
def get_and_validate_input(input_message, input_constraints):
    """
    This function implements input validation it an infinite loop.
    It makes the source code of a cli tool more readable and cleaner.
    """

    # get the first input
    instruction = input(input_message)

    # have a look on wheather it is a valid input or not
    while not validate_input(instruction, input_constraints):

        # while it is not valid, let user restate the input
        instruction = input(input_message)

    # return a valid user input
    return instruction

def get_and_validate_file_input(instruction, input_constraints):
    """
    This function implements input validation it an infinite loop.
    It makes the source code of a cli tool more readable and cleaner.
    """

    # get the first input

    # have a look on wheather it is a valid input or not
    if not validate_input(instruction, input_constraints):

        # while it is not valid, let user restate the input
        print("Input file degenerated.")

    # return a valid user input
    return instruction


########## machine / secondary storage interaction ##########

def get_file_design_parameter_domain(file_instruction):
    """
    This functions asks the user to state the value ranges of design parameters.
    It has two modes of operation:

    - direct declaration
        In this mode, the user must declare the value range stating integers or floats directly.
        The user is not to use blank spaces alongside commas to delimit the vlaues from one another.

    - declaration via closed interval(mathematics like intervals)
        In this mode, the user must define three values: upper_bound, lower_bound and stepsize.
        The step size must be a smaller value than the difference between upper_bound to lower_bound.
        The upper_bound and lower_bound can not be the same value.
        The values will be spread linearly except the upper_bound which will always be included.
        This mode is great for stating large value ranges.
    
    The function can also accept a single value, it will check wheather it can typecast it though.
    """

    # make sure user input is rather clean
    input_constraints = {
        'keywords': ["exit"],
        'allowed_characters':  ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ",", " ", "."],
        'disallowed_characters': [],
        'delimiters': [",", " "]
    }

    # the request message gives clear instructions about the modes and examples of the correct input format


    # get clean user input
    instruction = get_and_validate_file_input(file_instruction, input_constraints)

    # this is a redundant exit clause, it could be deleted but it doesnt harm anyone so why should we?
    if instruction == "exit":
        exit()
    
    # computing the desing parameter value range, this is a loop since the input can still be errornous
    design_parameter_list = []
    while design_parameter_list == []:
        try:
    
            # direct declaration mode
            if "," in instruction:

                # accept the value range directly but check for castability
                for value in instruction.split(','):
                    design_parameter_list.append(float(value))

            # declaration via closed interval mode
            elif " " in instruction:

                # get the requiered values
                lower_upper_step = instruction.split(' ')
                lower_limit = float(lower_upper_step[0])
                upper_limit = float(lower_upper_step[1])
                stepsize = float(lower_upper_step[2])

                # catch invalid inputs that are function specific
                if lower_limit <= upper_limit and  stepsize < (upper_limit - lower_limit):
                    stepsize_digits = len(lower_upper_step[2])
                    values_n = int(round(((upper_limit - lower_limit) / stepsize), stepsize_digits)) + 1
                    design_parameter_list = [round(lower_limit + index * stepsize, stepsize_digits) for index in range(values_n)]
                    design_parameter_list.append(upper_limit)
                else:

                    # if the constraints arent met, the instruction must be restated
                    print("\nInput file degenerated.")
            
            # single value input
            else:

                # check wheather the value can be typecasted
                value = float(instruction)
                design_parameter_list.append(value)

        except:

            # if the function still can not process the input it will ask for it again, who knows what went wrong
            print("\nInvalid input, please restate your instruction.")
            
    return design_parameter_list

def control_data_string_dict(file_control, data_name, export_calls=True):
    """
    This function can read the control file and will return certain sections of it as a dictionary object.
    The file will first look for the data name,
    Once it found it it will catch the lines until it reads 'END DATA'
    Once it has the lines, it will delimit them with the tabulator '\t'
    The first entry of this list is used as the key of a dictionary entry
    The rest of this list is used as its value
    This is optimized for use in the simulate function
    """

    #
    keys = []
    values = []
    section_found = False
    start_found = False

    # open the control file
    with open(file_control, 'r') as control_file:
        control_content = [line for line in control_file.readlines()]

    # look through all the lines  of the file
    for line in control_content:
        line_content = line[:-1].split('\t')

        # first check for termination constraint such that END DATA will not be part of the output
        if start_found and line_content[0] == "END DATA":
            break

        # if the first entry is the data_name, set section found to true and start data collection
        if line_content[0] == data_name:
            section_found = True

        # if the section has been found, look for start, then collect data
        if section_found:

            # collect data in the way described earlier
            if start_found:

                # data name as key and data content as value
                design_parameter_name = line_content[0]
                design_parameter_arguments = line_content[1:]
                control_string = ""
               
                # filter out empty cells from the tsv file
                for argument in design_parameter_arguments:
                    if argument == '' or argument == ' ':
                        continue

                    # set the arguments apart by blank spaces, this is optimized for use in simulation
                    control_string = control_string + str(argument) + " "
               
                # pop off the new_line character
                control_string = control_string[:-1]
                keys.append(design_parameter_name)
                values.append(control_string)

            # declare the start to be found before collection data, such that START is not part of the output
            if line_content[0] == "START":
                start_found = True

    # make a dictionary from the content
    editing_commands = dict(zip(keys, values))

    # choose wheather to export the keys seperatly from the dictionary
    if export_calls:
        return editing_commands, keys
    else:
        return editing_commands
   
def control_data_tuple_dict(control_file, data_name, export_calls=True):
    keys = []
    values = []
    section_found = False
    start_found = False

    # open the control file
    with open(control_file, 'r') as control_file:
        control_content = [line for line in control_file.readlines()]

    # look through all the lines  of the file
    for line in control_content:
        line_content = line[:-1].split('\t')

        # first check for termination constraint such that END DATA will not be part of the output
        if start_found and line_content[0] == "END DATA":
            break

        # if the first entry is the data_name, set section found to true and start data collection
        if line_content[0] == data_name:
            section_found = True

        # if the section has been found, look for start, then collect data
        if section_found:

            # collect data in the way described earlier
            if start_found:
                # data name as key and data content as value
                data_name = line_content[0]
                line_content_tuple = tuple(line_content[1:])
                keys.append(data_name)
                values.append(line_content_tuple)

            # declare the start to be found before collection data, such that START is not part of the output
            if line_content[0] == "START":
                start_found = True

    # make a dictionary from the content
    editing_commands = dict(zip(keys, values))

    # choose wheather to export the keys seperatly from the dictionary
    if export_calls:
        return editing_commands, keys
    else:
        return editing_commands




######### machine / human interaction ##########



def request_design_parameter_domain(design_parameter_name: str):
    """
    This functions asks the user to state the value ranges of design parameters.
    It has two modes of operation:

    - direct declaration
        In this mode, the user must declare the value range stating integers or floats directly.
        The user is not to use blank spaces alongside commas to delimit the vlaues from one another.

    - declaration via closed interval(mathematics like intervals)
        In this mode, the user must define three values: upper_bound, lower_bound and stepsize.
        The step size must be a smaller value than the difference between upper_bound to lower_bound.
        The upper_bound and lower_bound can not be the same value.
        The values will be spread linearly except the upper_bound which will always be included.
        This mode is great for stating large value ranges.
    
    The function can also accept a single value, it will check wheather it can typecast it though.
    """

    # make sure user input is rather clean
    input_constraints = {
        'keywords': ["exit"],
        'allowed_characters':  ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ",", " ", "."],
        'disallowed_characters': [],
        'delimiters': [",", " "]
    }

    # the request message gives clear instructions about the modes and examples of the correct input format
    request_message = f"""
    Define the value domain of {design_parameter_name}.

    Either state each value individually:
    <value 1>, <value_2>,<value_3>,<value_4>

    OR

    State a lower and upper bound and a step size 
    to define the value range as a closed intervall:
    <lower_bound> <upper_bound> <step_size>
    
    {design_parameter_name}: """

    # get clean user input
    instruction = get_and_validate_input(request_message, input_constraints)

    # this is a redundant exit clause, it could be deleted but it doesnt harm anyone so why should we?
    if instruction == "exit":
        exit()
    
    # computing the desing parameter value range, this is a loop since the input can still be errornous
    design_parameter_list = []
    while design_parameter_list == []:
        try:
    
            # direct declaration mode
            if "," in instruction:

                # accept the value range directly but check for castability
                for value in instruction.split(','):
                    design_parameter_list.append(float(value))

            # declaration via closed interval mode
            elif " " in instruction:

                # get the requiered values
                lower_upper_step = instruction.split(' ')
                lower_limit = float(lower_upper_step[0])
                upper_limit = float(lower_upper_step[1])
                stepsize = float(lower_upper_step[2])

                # catch invalid inputs that are function specific
                if lower_limit <= upper_limit and  stepsize < (upper_limit - lower_limit):
                    stepsize_digits = len(lower_upper_step[2])
                    values_n = int(round(((upper_limit - lower_limit) / stepsize), stepsize_digits)) + 1
                    design_parameter_list = [round(lower_limit + index * stepsize, stepsize_digits) for index in range(values_n)]
                    design_parameter_list.append(upper_limit)
                else:

                    # if the constraints arent met, the instruction must be restated
                    print("\nInvalid input, please restate your instruction. \nPerhabs you have defined a interval with length 1 as in '1 1 1'.")
                    instruction = get_and_validate_input(request_message, input_constraints)
            
            # single value input
            else:

                # check wheather the value can be typecasted
                value = float(instruction)
                design_parameter_list.append(value)

        except:

            # if the function still can not process the input it will ask for it again, who knows what went wrong
            print("\nInvalid input, please restate your instruction.")
            instruction = get_and_validate_input(request_message, input_constraints)
            
    # give feedback about the value range that has been created
    print(f"\nValues {design_parameter_name}:\n", design_parameter_list)
    print("\nMistakes can be fixed in the next step.\n\n")

    return design_parameter_list



########## machine / machine interaction ##########



def slave_mode(file_dat_path):
    """
    This is a server function that can accept connection attempts from a client which in this chase is the simulation master machine.
    The simulation master machine handles any conciderations about keeping track of the simulation series by updating the joblist file, 
    handing out jobs to slave machines in order to keep them busy and gathering the results in a result file or result folder.
    
    - Once this mode is chosen, you will see the socket information of this machine as a print output.
    - Take this socket information as an Input for the master machine and you will connect the two machines as master and slave machines.
    - If the connection was successful, you will see a confirmation on the screen of this machine.
    - Use SSH to gain comfort when using this mode.
    
    Since in this mode, there are always more than one machine active, it is a good idea to add redundant storage and let each machine
    write a backup of ALL results to their disk regularly. There is no reason not to do this since the hardware is certainly available
    in this mode and as everyone in IT knows: 'two is one and one in none', so lets not risk our valuable data.
    """

    time.sleep(5)
    return "done"
    ON = True
    sock = socket.socket()
    socket.bind(('', 0))
    socket_number = sock.getsockname()[1]
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"\nYou are now using EDG in slave mode.\nPlease connect master to following Socket address:\n\nSocketnumber: {socket_number}\nIP Address: {ip_address}\n")
    while ON:
        sock.listen()
        connection, address = sock.accept()
        job = connection.recv()
        result_entry = simulation.simulate(job, file_dat_path, file_dat_path, "slave")
        connection.send(result_entry)
    
