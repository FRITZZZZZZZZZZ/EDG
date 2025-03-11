import interaction

def write_blank_session_file(design_parameter_names, session_file_backup_path):
    # read the backup session file
    with open(session_file_backup_path, 'r') as session_file_backup:
        session_file_backup_content = [line for line in session_file_backup.readlines()]
    
    # create a new session file string
    new_session_file = ""
    design_parameter_section_found = False
    for line in session_file_backup_content:
        new_session_file += line
        if design_parameter_section_found:
            # append a list of design parameters to the session file in the correct oder
            for parameter_name in design_parameter_names:
                new_session_file += f"{parameter_name}\n<your_design_parameter_value_range>\n"
            new_session_file += "END DATA\n"
            design_parameter_section_found = False
        # notice once the design parameter section has been found
        if "DESIGN PARAMETER NAMES AND RANGES" in line:
            design_parameter_section_found = True
    
    with open("blank_session_file.txt", 'w') as session_file:
        session_file.write(new_session_file)

def read_session_file(session_file_path):
    # gather the session file content
    with open(session_file_path, 'r') as session_file:
        session_file_content = [line for line in session_file.readlines()]
    # ignore anything with a # in it and also ignore the next line character
    session_file_data = []
    for line in session_file_content:
        line = line[:-1]
        if "#" in line or line == "":
            continue
        session_file_data.append(line)

    # pre define all the values that will be exportet
    simulation_time_limit = None
    simulation_loop_limit = None
    base_name = None
    design_parameter_domains = None
    slave_sockets = None
    participation = None

    # catch the simulation time limit
    simulation_time_limit_next = False
    for line in session_file_data:
        if simulation_time_limit_next:
            simulation_time_limit = line
            break
        if "SIMULATION TIME LIMIT" in line:
            simulation_time_limit_next = True

    # catch the simulation loop limit
    simulation_loop_limit_next = False
    for line in session_file_data:
        if simulation_loop_limit_next:
            simulation_loop_limit = line
            break
        if "SIMULATION LOOP LIMIT" in line:
            simulation_loop_limit_next = True

    # catch the base name
    base_name_next = False
    for line in session_file_data:
        if base_name_next:
            base_name = line
            break
        if "BASE NAME" in line:
            base_name_next = True

    # catch the design parameter value lists
    design_parameter_names = []
    design_parameter_value_ranges = []
    design_parameter_section_found = False
    name_next = False
    values_next = False
    for line in session_file_data:
        if "END DATA" in line and design_parameter_section_found:
            break
        if "DESIGN PARAMETER NAMES AND RANGES" in line:
            design_parameter_section_found = True
            name_next = True
            continue
        # alternate between catching a name and catching a value range
        if name_next:
            design_parameter_names.append(line)
            name_next = False
            values_next = True
            continue
        if values_next:
            design_parameter_value_ranges.append(interaction.get_file_design_parameter_domain(line))
            values_next = False
            name_next = True
            continue
    # the design parameter list should be none if it is empty
    if len(design_parameter_value_ranges) > 0:
        design_parameter_domains = design_parameter_value_ranges
    
    # catch the slave socket lists
    slave_socket_list = []
    slave_socket_section_found = False
    for line in session_file_data:
        if "END DATA" in line and slave_socket_section_found:
            break
        if slave_socket_section_found:
            slave_socket_list.append(line)
        if "SLAVE SOCKETS" in line:
            slave_socket_section_found = True
    # the slave socket list should be none if it is empty
    if len(slave_socket_list) > 0:
        slave_sockets = slave_socket_list

    # catch the participation decision
    participation_next = False
    for line in session_file_data:
        if participation_next:
            participation_decision = line
            if participation_decision == "Y":
                participation = True
            if participation_decision == "n":
                participation = False
            break
        if "BASE NAME" in line:
            participation_next = True

    return [simulation_time_limit, simulation_loop_limit, base_name, design_parameter_domains, slave_sockets, participation]

