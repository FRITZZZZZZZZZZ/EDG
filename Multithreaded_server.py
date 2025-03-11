import threading
import socket
import json
import time
import simulation_management
import job_management


def master_socket(slave_ip, slave_port, thread_index):

    # helper function to terminate socket threads
    def delete_value(array, value):
        array_edited = []
        for array_index in range(len(array)):
            if array[array_index] == value:
                continue
            array_edited.append(array[array_index])
        return array_edited

    # control variables for socket threads
    global job_pool
    global slave_ip_addresses
    global slave_port_numbers
    global connected

    # connect to a slave machine and mark thread as connected
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((HOST, 0))
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

def host_simulation(thread_index):
    while True:
        if job_pool[thread_index] != None:
            job = job_pool[thread_index]
            result = simulation_management.(job)
            job_pool[thread_index] = None      

def master_job_manager(joblist):
    global job_pool
    job_list_index = 0
    while job_list_index < len(joblist):
        job = joblist[job_list_index]
        for job_pool_index in range(len(job_pool)):
            if job_pool[job_pool_index] == None and not "NOT AVAILABLE":
                job_pool[job_pool_index] = job
                job['status'] = "in progress"
                job_list_index += 1
                continue
        if job_list_index == len(joblist):
            break

def multithread_server():            
    HOST = socket.gethostbyname(socket.gethostname())

    thread_list = []
    job_pool = []
    thread_control = []
    slave_ip_addresses = []
    slave_port_numbers = []
    connected = []
    thread_index = 0
    done = False
    Start = False
    joblist = create_jobs("jobname", "pending",[1,2,3],[1,2,3],[1,2,3],[1,2,3],[1,2,3],[1,2,3])
    # create the master slave connections
    while not done:
        print("\nState IP Adress and Port number of EDG Slave in the exact Format <IP_Adress> <Port_Number>, state 'done' to continue.\n")
        instruction = input("<IP_Adress> <Port_Number>: ")
        try:
            if instruction == "done":
                done = True
                thread_list.append(threading.Thread(target=master_job_manager, args=[joblist]))
                break
            slave_ip = instruction.split(' ')[0]
            slave_port = int(instruction.split(' ')[1])
            job_pool.append(None)
            thread_control.append(True)
            slave_ip_addresses.append(slave_ip)
            slave_port_numbers.append(slave_port)
            connected.append(False)
            thread_list.append(threading.Thread(target=master_socket, args=[slave_ip, slave_port, thread_index]))
            thread_index += 1
            thread_list[-1].start()
        except:
            print("invalid input")
            print("State IP Adress and Port number of EDG Slave in the exact Format <IP_Adress> <Port_Number> or state 'exit' to exit.")
            instruction = input("<IP_Adress> <Port_Number>: ")
    # wait for all slaves to be connected
    if False in connected:
        print("Waiting for connection or connection timeout")
        wait_counter = 0
        while False in connected:
            time.sleep(0.02)
            wait_counter += 1
            if wait_counter % 50 == 0:
                print(f"still waiting, {int((500 - wait_counter)/50)} seconds to go")
            if wait_counter > 500:
                break
    # allow changes to slave cluster and allow self participation
    if None in job_pool:
        for connection_index in range(len(slave_ip_addresses)):
            print(f"slave number {connection_index} ip {slave_ip_addresses[connection_index]} port {slave_port_numbers[connection_index]}")
        instruction = input("Do you want to use the host machine to generate Data too?\nThis option may slow down your machine and be very power hungry!\n[Y/n]")
        if instruction == "Y":
            job_pool.append(None)
            thread_control.append(True)
            thread_list.append(threading.Thread(target=host_simulation, args=[thread_index]))
            thread_index += 1
            thread_list[-1].start()
        instruction = input("Do you want to start the data generation process?[Y/n]")
        if instruction == "Y":
            thread_list[-1].start()
    else:
        print("No Slave could be connected")




