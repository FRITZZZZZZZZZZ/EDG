import socket
import simulation_management

def simulation_slave():
    # retrieve the slave IP address
    HOST = socket.gethostbyname(socket.gethostname())

    # open a TCP socket and bind to any open port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))

        # give socket information to user in order to connect master to slave
        IP = sock.getsockname()[0]
        PORT = sock.getsockname()[1]
        print("\nThe Simulation slave machine is listening\n")
        print(f"\nIP: {IP} PORT: {PORT}\n")

        # wait for master to connect
        sock.listen()
        connection, master_addrress = sock.accept()

        # receive packages from the master machine
        while True:
            message = connection.recv(1024)
            print(message)
            connection.sendall(f"done".encode('utf-8'))

string = ""
print(string.__sizeof__(), len(string))