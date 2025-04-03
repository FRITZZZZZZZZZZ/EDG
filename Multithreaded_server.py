import threading
import socket
import json
import time
import simulation_management
import job_management
import interaction


def master_socket(slave_ip, slave_port, thread_index):

    # helper function to terminate socket threads
    def delete_value(array, value):
        array_edited = []
        for array_index in range(len(array)):
            if array[array_index] == value:
                continue
            array_edited.append(array[array_index])
        return array_edited

    local_ip = socket.gethostbyname(socket.gethostname())

    # control variables for socket threads
    global job_pool
    global connected

    # connect to a slave machine and mark thread as connected
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((local_ip, 0))
            sock.connect((slave_ip, slave_port))
            connected[thread_index] = True

            # while on, look at the job index and try to simulate the job if one is there
            while True:
                time.sleep(1)
                if job_pool[thread_index] != None:

                    # pick up the job and send to the slave machine as a json
                    job = job_pool[thread_index]
                    json_job = json.dumps(job, indent=4)
                    sock.sendall(json_job.encode())
                    
                    # receive the result and write it to the result index
                    simulation_result = sock.recv(1024)
                    job_pool[thread_index] = None
                
                # if the job index is False, end the process
                if job_pool[thread_index] == False:
                    sock.close()
                    break
    except:
        connected[thread_index] = "NOT AVAILABLE"
        # all the threads would need their thread_index updated, therefore it is easier to just state them as NOT AVAILABLE
        job_pool[thread_index] = "NOT AVAILABLE"
        slave_port_numbers = delete_value(slave_port_numbers, slave_port)
        slave_ip_addresses = delete_value(slave_ip_addresses, slave_ip)
   


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
        thread_list.append(threading.Thread(target=master_socket, args=[slave_ip, slave_port, thread_index]))
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
                job_pool.append(None)
                # increment the thread index and start the master thread
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