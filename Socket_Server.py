import socket
import pickle

import select


def new_connection(ip_address, port=5005):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_address, port))
    s.listen()
    return s


def receive_object(socket):
    inputs, outputs, errors = select.select([socket], [], [socket], 6)
    for socket in inputs:
        new_socket, addr = socket.accept()
        all_data = b''
        while True:
            data = new_socket.recv(4092)
            if not data:
                break
            all_data += data
        return pickle.loads(all_data)
    else:
        return None


if __name__ == "__main__":
    localhost_conn = new_connection('localhost')
    message = receive_object(localhost_conn)

    print(message.data[0])
    print(message.data[1])

    if message.is_valid():
        print('Success, transaction is valid')
    else:
        print('ERROR, transaction NOT valid')

    if message.data[0].inputs[0][1] == 2.3:
        print('Success, transaction value matches')
    else:
        print('ERROR, transaction value DOES NOT match')
        
    new_message = receive_object(localhost_conn)
