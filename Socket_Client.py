import socket

import TransactionBlock
from Transaction import Transaction
from Signatures import generate_keys
import pickle


def send_object(ip_address: str, block: object, tcp_port: int = 5005) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_address, tcp_port))
    s.send(pickle.dumps(block))
    s.close()
    return True


if __name__ == '__main__':
    private_key1, public_key1 = generate_keys()
    private_key2, public_key2 = generate_keys()
    private_key3, public_key3 = generate_keys()

    transaction1 = Transaction()
    transaction1.add_input(public_key1, 2.3)
    transaction1.add_output(public_key2, 1.0)
    transaction1.add_output(public_key3, 1.1)
    transaction1.sign(private_key1)

    transaction2 = Transaction()
    transaction2.add_input(public_key2, 2.3)
    transaction2.add_input(public_key3, 1.0)
    transaction2.add_output(public_key1, 3.1)
    transaction2.sign(private_key2)
    transaction2.sign(private_key3)

    block1 = TransactionBlock.TransactionBlock(None)
    block1.addTransaction(transaction1)
    block1.addTransaction(transaction2)

    send_object('localhost', block1)
