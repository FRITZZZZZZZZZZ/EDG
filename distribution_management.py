import threading
import socket
import json
import time
import simulation_management
import job_management
import interaction
import distribution_management
import os
import threading
import socket
import time
import os
import sys


def receive_message(connection, previous_message):
    current_message = connection.recv(1024)
    buffer_window = None
    # another message has been received, concatenate them and extract the content
    if not previous_message == None:
        buffer_window = previous_message + current_message
        previous_message = current_message
    # base chase, no message has been received yet
    if buffer_window == None:
        previous_message = current_message
        buffer_window = current_message
    return buffer_window

def send_data(sock, data_path):
    """
    This function takes a socket, a path to a file or directory and if necessery a file role if requiered.
    If the data_path only leads to a file, it will just send the file. If it is a directory tho, the function
    will send every single file contained in the directory and if there is another directory in the directory,
    it will send this directory too.
    """

    def send_file(sock, file_path):
        """
        This function implements a simple protocol to send data to another machine. 
        It can send any file type and gives meta information about the files role, suffix, size and name.
        """
        # gather header and file data
        with open(file_path, 'rb') as file:
            file_data = file.read()
        file_name = file_path.split('/')[-1]

        # send the data
        sock.send(f"__FILETRANSFER {file_name}\n__START_DATA".encode())
        sock.sendall(file_data)
        sock.send("__END_DATA".encode())


    def send_directory(sock, directory_relative_path):
        """
        This function is used to send a directory path to another machine in order for the machine 
        to instanciate the directory in chase it does not yet exist.
        """
        # make the directory transfer command and send it, actually this did not need its own function but i made one for symmetry anyway, there you go
        directory_request = f"__DIRECTORY_REQUEST {directory_relative_path}\n".encode()
        sock.send(directory_request)

    # multi line flags
    start_transfer_flag = b'__DATATRANSFER'
    end_transfer_flag = b'__END_DATATRANSFER'

    # control variables
    path_list = []
    relative_path = ""
    directory_file_lists = []
    
    # announce the datatransfer
    sock.send(start_transfer_flag)

    # if the path leads to a directory, send it and note which files are in it, these will be send in the next step
    initial_item = data_path.split('/')[-1]
    if os.path.isdir(data_path):
        path_list.append(initial_item)
        relative_path += initial_item
        send_directory(sock, relative_path)
        directory_file_lists.append(os.listdir(data_path))

        for directory in path_list:
            path_index = path_list.index(directory)
            directory_list = directory_file_lists[path_index]
            new_directory_found = False
            for item in directory_list:

                # if the item is another directoy, make another directory list and go on
                if os.path.isdir(item):
                    path_list.append(item)
                    relative_path = '/'.join(path_list)
                    send_directory(sock, relative_path)
                    directory_file_lists.append(os.listdir(relative_path))
                    new_directory_found = True
                    break
                
                # if the item is just a file
                else:
                    item_path = fr"{relative_path}/{item}"
                    send_file(sock, item_path)
            
            if not new_directory_found:
                path_list = path_list[:-1]
                relative_path = '/'.join(path_list)
    else:
        # if the path leads to a single file just send this one and you are done
        send_file(sock, data_path)
    
    sock.send(end_transfer_flag)

def receive_data(connection, last_message, target_directory):
    """
    This function can receive files and complete directories via socket that follows the correct protocoll
    """
    # multi line flags
    start_transfer_flag = b'__DATATRANSFER'
    end_transfer_flag = b'__END_DATATRANSFER'
    start_data_flag = b'__START_DATA'
    end_data_flag = b'__END_DATA'
    # inline flags
    directory_request_flag = b'__DIRECTORY_REQUEST'
    file_transfer_flag = b'__FILETRANSFER'
    end_inline_flag = b'\n'

    start_index_datatransfer = last_message.index(start_transfer_flag) + len(start_transfer_flag)
    message = last_message[start_index_datatransfer :]

    while True:
        # catch a directory request, continue receiiving data if it is not completly buffered
        if directory_request_flag in message:
            try:
                request_start = message.index(directory_request_flag)
                request_end = message.index(end_inline_flag)
                request_section = message[request_start : request_end]
                request = request_section.decode()
                directory_path = request[-1]
                # check if the directory exists, if not create it
                if not os.path.isdir(f"{target_directory}/{directory_path}"):
                    os.mkdir(f"{target_directory}/{directory_path}")
                # pop the directory request section from the message and continue
                request_end_index = request_end + len(end_inline_flag)
                message = message[: request_start] + message[request_end_index :]
                continue
            except:
                continue

        # catch a file transfer, 
        if file_transfer_flag in message:
            file_name = None
            try:
                file_command_start = message.index(file_transfer_flag)
                file_command_end = message.index(end_inline_flag)
                file_command_section = message[file_command_start : file_command_end]
                file_command = file_command_section.decode()
                file_name = file_command.split(' ')[-1]
            except:
                continue

            # catch the data from the connection buffer
            file_data = None
            data_start_index = None
            data_end_index = None
            while True:
                # initialize the data collection
                if start_data_flag in message:
                    data_start_index = message.index(start_data_flag) + len(start_data_flag)

                # write the file if the end flag is spotted
                if end_data_flag in message:
                    data_end_index = message.index(end_data_flag)
                    # catch the chase that all file data is in one buffer
                    if not data_start_index == None:
                        file_data = message[data_start_index:data_end_index]
                    else:
                        file_data += message[:data_end_index]
                    # write the file data to a file
                    with open(f"{target_directory}/{file_name}", 'wb') as file:
                        file.write(file_data)
                    # reinitialize the file variables and pop the file transfer from the message
                    file_transfer_end_index = message.index(end_data_flag) + len(end_data_flag)
                    message = message[file_transfer_end_index :]
                    data_start_index = None
                    data_end_index = None
                    break

                # if there is not end data flag in the data, add all to the file data and get next message
                if not data_start_index == None:
                    file_data = message[data_start_index:]
                    data_start_index == None
                else:
                    file_data += message
                
                # get the next buffer
                message = receive_message(connection, previous_message)
                previous_message = message
                
        # if the stop transfer flag is contained in the message, stop the datatransfer, this branch is only reached if no directory or filetransfer is spotted
        if end_transfer_flag in message:
            try:
                transfer_end_index = message.index(end_transfer_flag) + len(end_transfer_flag)
                message = message[transfer_end_index :]
                return message
            except:
                pass

        previous_message = message
        message = receive_message(connection, previous_message)

def master(slave_ip, slave_port, thread_index):
    """
    This is a function that can communicate with another machine via TCP and transfer files back and forth, hand out simulation jobs and declare
    files as raw files so the slave machine does use the correct files for the simulation.
    """
    # helper function to terminate socket threads
    def delete_value(array, value):
        array_edited = []
        for array_index in range(len(array)):
            if array[array_index] == value:
                continue
            array_edited.append(array[array_index])
        return array_edited

    # control structures
    global job_pool
    global connected

    # establish a connection
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            address_self = socket.gethostbyname(socket.gethostname())
            sock.bind((address_self, 0))
            sock.connect((slave_ip, slave_port))

            # send state such that the slave machines pre processing direcory is the same as the master ones
            send_data(sock, r"pre_processing_programs")
            send_data(sock, r"simulation_solving_programs")
            send_data(sock, r"control_file.tsv")
            os.mkdir(f"slave_{thread_index}_results")
            connected[thread_index] = True

            # wait for furthter instructions
            while True:
                # terminate the connection
                if instruction == False:
                    break

                # pack and send the job to the slave machine
                instruction = job_pool[thread_index]

                # if the instruction is a job, send it to the slave machine
                if type(instruction) == dict:
                    job = instruction
                    send_data()
                    # mark self as idle again

                # receive the job result files or failure message

                # move the result data to the correct directory
                

                # declare self as idle and wait for next job
                job_pool[thread_index] == None
        
                time.sleep(1)   

            # turn off simulation slave
        return
    
    except:
        # all the threads would need their thread_index updated, therefore it is easier to just state them as NOT AVAILABLE
        connected[thread_index] = "NOT AVAILABLE"
        job_pool[thread_index] = "NOT AVAILABLE"
        slave_port_numbers = delete_value(slave_port_numbers, slave_port)
        slave_ip_addresses = delete_value(slave_ip_addresses, slave_ip)


def slave():
    """
    This is a function that can communicate with a master thread to receive jobs to simulate, start simulations and 
    transfer files back and forth.
    """   
    def simulate_job(connection, message):
        """
        This function takes a message containg the job flag, extracts the job data and simulates the job.
        Then it uses the connection to send back the result files or the unsuccessfull flag
        """
        # flags
        start_job_flag = b"__JOB"
        end_job_flag = b"__END_JOB"
        
        # fetch the whole job
        job_message = None
        while True:
            # if the job is completly contained in the message
            if end_job_flag in message and start_job_flag in message:
                job_message = message[start_job_flag:end_job_flag]
                job_end_index = message.index(end_job_flag) + len(end_job_flag)
                message = message[:start_job_flag] + message[job_end_index:]
                break
            previous_message = message
            message = receive_message(connection, previous_message)

        

    # establish a connection find out own address bind to any open port and display socket info
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        address_self = socket.gethostbyname(socket.gethostname())
        sock.bind((address_self, 0))
        port_self = sock.getsockname()[1]
        print(f"\nIP: {address_self}, PORT {port_self}")

        # listen to and process instruction messages, each message processing function will return the rest of the message which was not of interest
        sock.listen()
        connection, master_address = sock.accept()
        print("CONNECTED")
        with connection:
            # if there are files missing or not the same as on the master machine, a datatransfer is done to update these files
            previous_message = None
            message = receive_message(connection, previous_message)
            while True:
                # transfer files like raw dat file or raw t51 file
                if b'__DATATRANSFER' in message:
                    message = receive_data(connection, message)     
                # receive a job, simulate it and send back its result files           
                if b'__JOB' in message:
                    message = simulate_job(connection, message)
                # end the slave mode 
                if b'__END' in message:
                    break
                # get the next message
                previous_message = message
                message = receive_message(connection, previous_message)
    return    




def multithread_server(job_tuple):  

    def simulate_self(thread_index):
        global job_pool
        while True:
            instruction = job_pool[thread_index]
            # terminate the connection
            if instruction == False:
                break

            if type(instruction) == dict:
                # solve the job
                job = instruction
                success_solving = simulation_management.simulate(instruction)
                # mark self as idle again
                job_pool[thread_index] == None
            time.sleep(1)              

    def start_connection(instruction, thread_index, connected):
        # extract slave address and port
        try:
            slave_ip = instruction.split(' ')[0]
            slave_port = int(instruction.split(' ')[1])
        except:
            print("\nNo valid socket data found, please stick to given format.\n")
            return False
        # prepare the master thread environment
        job_pool.append(None)
        slave_ip_addresses.append(slave_ip)
        slave_port_numbers.append(slave_port)
        connected.append(False)
        # increment the thread index and start the master thread
        thread_list.append(threading.Thread(target=master, args=[slave_ip, slave_port, thread_index]))
        thread_index = thread_index + 1
        #thread_list[-1].start()
        return thread_index

    def confirm_connections(slave_ip_addresses, slave_port_numbers, connected, thread_index, connection_time_limit=20):
        # wait for all slaves to be connected
        if False in connected:
            print("Waiting for connection or connection timeout")
            wait_counter = 0
            while False in connected:
                time.sleep(1)
                wait_counter += 1
                if wait_counter % 10 == 0:
                    print(f"still waiting, {connection_time_limit - wait_counter} seconds to go")
                if wait_counter > connection_time_limit:
                    break
        if None in job_pool:
            for connection_index in range(thread_index):
                if connected[thread_index] == True:
                    print(f"Slave number {connection_index} ip {slave_ip_addresses[connection_index]} port {slave_port_numbers[connection_index]} is connected.")
                else:
                    print(f"Slave number {connection_index} ip {slave_ip_addresses[connection_index]} port {slave_port_numbers[connection_index]} is NOT connected.")
        else:
            print("No Slave could be connected")

    def connect_slave_machines(slave_ip_addresses, slave_port_numbers, connected, thread_index):
        while True:
            while True:
                # get the socket information from the user
                slave_socket_constraint = {'keywords':["c", "-c", "continue"], 'allowed_characters': ["0","1","2","3","4","5","6","7","8","9", ".", " "]}
                instruction = interaction.get_and_validate_input(ask_slave_socket, slave_socket_constraint)
                # exit and append the job manager
                if instruction == "c" and len(slave_ip_addresses)>0 and len(slave_port_numbers)>0:
                    confirm_connections(slave_ip_addresses, slave_port_numbers, connected, thread_index)
                    # allow reconnection
                    reconnect_constraint = {'keywords':["Y", "n"]}
                    instruction = interaction.get_and_validate_input("\nDo you want to try and reconnect a slave machine?\n\n[Y/n] ", reconnect_constraint)
                    if instruction == "Y":
                        continue
                    if instruction == "n":
                        break
                # try to establish the connection to the slave machine
                thread_index = start_connection(instruction, thread_index, connected)
        
            # let user decide to use master machine for simulation too
            simulate_self_constraint = {'keywords':["Y", "n"]}
            instruction = interaction.get_and_validate_input("\nWould you like to use the local machine for simulation as well?\nThis may slow down your machine.\n\n[Y/n] ", simulate_self_constraint)
            
            if instruction == "Y":
                # increment the thread index and start the master thread
                job_pool.append(None)
                thread_list.append(threading.Thread(target=simulate_self, args=[thread_index]))
                thread_index = thread_index + 1
                thread_list[-1].start()
            
            if instruction == "n":
                pass
                
            # let user decide to make any last changes
            ask_start = "\nDo you want to start the data generation now?\nYou can edit your past choices when stating 'n'.\n\n[Y/n] "
            start_constraint = {'keywords':["Y", "n"]}
            instruction = interaction.get_and_validate_input(ask_start, start_constraint)

            if instruction == "Y":
                return
            
            if instruction == "n":
                continue

    ask_slave_socket = """
    State IP Adress and Port number of EDG Slave in the exact Format <IP_Adress> <Port_Number>, state '-c' to continue.
    <IP_Adress> <Port_Number>: """

    joblist, full_header, value_range_list = job_tuple
    local_ip = socket.gethostbyname(socket.gethostname())

    thread_list = []
    job_pool = []
    slave_ip_addresses = []
    slave_port_numbers = []
    connected = []
    thread_index = 0

    # create the master slave connections
    connect_slave_machines(slave_ip_addresses, slave_port_numbers, connected, thread_index)

multithread_server((None, None, None))
master_thread = threading.Thread(target=master, args=[])
slave_thread = threading.Thread(target=slave, args=[])

def run_trial():
    master_thread.start()
    slave_thread.start()

    master_thread.join()
    slave_thread.join()

run_trial()