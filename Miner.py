import Socket_Client
import Socket_Server
import TransactionBlock
import Transaction
import Signatures


class Miner_Server():
    transactions = []
    socket_server = None
    head_blocks = []

    def __init__(self, my_ip, wallet_list):
        self.my_ip = my_ip
        self.wallet_list = wallet_list

    def find_longest_blockchain(self):
        longest = -1
        long_head = None
        for b in self.head_blocks:
            current = b
            this_len = 0
            while current is not None:
                this_len += 1
                current = current.previous_block
            if this_len > longest:
                long_head = b
                longest = this_len
        return long_head

    def create_connection(self):
        # open server connection
        self.socket_server = Socket_Server.new_connection(self.my_ip)

    def receive_transactions(self):
        # receive transactions
        while True:
            received = Socket_Server.receive_object(self.socket_server)
            print('Received transaction: ', received)
            if received is None:
                break
            if isinstance(received, Transaction.Transaction):
                self.transactions.append(received)
        self.socket_server.close()

        if len(self.transactions) == 0:
            print('No transactions to put in block, quitting.')
            return

    def collect_transactions(self):
        # collect transactions into block
        block = TransactionBlock.TransactionBlock(self.find_longest_blockchain())
        for transaction in self.transactions:
            block.addTransaction(transaction)

        print('block: ', block)
        print('block is valid: ', block.is_valid())
        return block

    def mine_block(self, block):
        # find nonce
        print('Start mining block')
        block.find_nonce()

        if not block.good_nonce():
            print('Error: could not find a good nonce, quitting.')
            return
        return block

    def send_response(self, block):
        # send that block to each in wallet_list
        for ip in self.wallet_list:
            success = Socket_Client.send_object(ip, block, 5000)
            if success:
                print('Block sent successfully')
            else:
                print('Block sending failed')


if __name__ == "__main__":
    miner = Miner_Server('localhost', ['localhost'])
    miner.create_connection()
    miner.receive_transactions()
    block = miner.collect_transactions()
    block = miner.mine_block(block)
    miner.send_response(block)

