import socket
import threading
import socket
import time

def beispiel():
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

def master():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        address_self = socket.gethostbyname(socket.gethostname())
        role_index = "dat\n"
        sock.bind((address_self, 0))
        sock.connect(("192.168.1.105",64001))
        sock.send("\nFILETRANSFER\n".encode())
        sock.send(f"{role_index}".encode())
        with open(r"CONTROL_FILE_BACKUP_DO_NOT_TOUCH.tsv", 'r') as file:
            file_content = file.read()
        sock.sendall(file_content.encode())
        sock.send("\nEND FILETRANSFER\n".encode())
    return

def slave():
    """
    This is a function that can communicate with a master thread to receive jobs to simulate, start simulations and 
    transfer files back and forth.
    """
    def file_receiver(connection, file_name):
        with connection:
            received_file = ""
            file_transfer = False
            next_name = True
            while True:
                message = connection.recv(1024).decode()
                print(message)
                if message == "FILETRANSFER":
                    next_role = True
                if next_name:
                    file_name = message
                    file_transfer = True
                if len(message) == 0:
                    file_transfer = False
                    with open(file_name, "w") as new_file:
                        new_file.write(received_file)
                    break
                if file_transfer:
                    received_file += message
    
    def write_content(file_name, content_list):
        file_content = ""
        for line in content_list:
            file_content += line + "\n"
        with open(file_name, 'w') as new_file:
            new_file.write(file_content)
        
    def handle_datastream(current_message, previous_message):
        buffer_window = None
        previous_message = None
        message_content = []
        # another message has been received, concatenate them and extract the content
        if not previous_message == None:
            buffer_window = previous_message + current_message
            message_content = buffer_window.split('\n')
            previous_message = current_message
        # base chase, no message has been received yet
        if buffer_window == None:
            previous_message = current_message
            message_content = current_message.split('\n')
        return message_content

    def receive_file(message_content, file_content, file_transfer):
        # detect a file transfer and append all message content to the file content list
        transfer_start = message_content.index("FILETRANSFER")
        role_index = transfer_start + 1
        content_start_index = transfer_start + 2
        # declare the file role and start to collect the file content
        file_role = message_content[role_index]
        file_content += message_content[content_start_index:]
        # detect that the file transfer is finished, append the last file section and write the file
        if "END FILETRANSFER" in message_content:
            content_end_index = message_content.index("END FILETRANSFER") - 1
            file_content += message_content[:content_end_index]
            file_transfer = False
            message_content = message_content[content_end_index:]
            write_content("file_", file_content) 
            return False           
        # append the message content to the file content
        if file_transfer:
            file_content += message_content
            return file_content, file_transfer

    # establish a connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # find out own address bind to any open port and display socket info
        address_self = socket.gethostbyname(socket.gethostname())
        sock.bind((address_self, 64001))
        print(address_self, sock.getsockname()[1])
        # listen and accept a connection
        sock.listen()
        connection, master_address = sock.accept()
        with connection:
            # buffer messages such that keywords are always received even if they are sent in two consecutive messages
            previous_message = None
            message_content = []
            file_transfer = True
            file_content = []
            file_role = None
            review = False
            while True:
                current_message = connection.recv(1024).decode()
                # if the message is empty, do nothing
                if current_message == "":
                    if not review:
                        continue
                    review = False
                # make sure that keywords are not seperated by transmission in seperate buffers
                message_content = handle_datastream(current_message, previous_message)
                # detect a file transfer and append all message content to the file content list
                file_content = receive_file(current_message, file_content)
                if not file_content:
                    review = True
                    continue

                time.sleep(1)
    return    

master = threading.Thread(target=master, args=[])
slave = threading.Thread(target=slave, args=[])

master.start()
slave.start()

master.join()
slave.join()