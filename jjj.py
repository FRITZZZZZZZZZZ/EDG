import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    own_address = socket.gethostbyname(socket.gethostname())
    sock.bind((own_address, 0))
    