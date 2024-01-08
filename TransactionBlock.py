import pickle
import random
import string
import time

from cryptography.hazmat.primitives import hashes

from Blockchain import CBlock
from Signatures import generate_keys
from Transaction import Transaction

REWARD = 25.0


class TransactionBlock(CBlock):
    checksum = None
    nonce = None
    difficulty = 19

    def __init__(self, previous_block):
        super(TransactionBlock, self).__init__([], previous_block)
        if previous_block is not None:
            self.checksum = previous_block.compute_hash()

    def addTransaction(self, transaction):
        self.data.append(transaction)

    def __count_totals(self):
        total_in = 0
        total_out = 0
        for transaction in self.data:
            for addr, amt in transaction.inputs:
                total_in += amt
            for addr, amt in transaction.outputs:
                total_out += amt

        return total_in, total_out

    def is_valid(self):
        if not super(TransactionBlock, self).is_valid():
            # print("Previous block doesn't match the hash")
            return False
        for transaction in self.data:
            if not transaction.is_valid():
                # print('Invalid transaction')
                return False
        total_in, total_out = self.__count_totals()
        # todo: should be using Decimal for transactions
        if total_out - total_in - REWARD > 0.00000000000001:
            # print(f'Greedy miner')
            return False
        return True
        # all transactions are valid
        # the checksum of previous block is valid

    def good_nonce(self):
        sha256 = hashes.Hash(hashes.SHA256())
        sha256.update(bytes(str(self.data), 'utf-8'))
        sha256.update(bytes(str(self.previous_hash), 'utf-8'))
        sha256.update(bytes(str(self.nonce), 'utf-8'))
        hash = sha256.finalize()

        hash_chars = ''.join(f'{char:08b}' for char in hash)
        # print(hash_chars)
        # for n, c in enumerate(hash):
        #     print(n, '{0:08b}'.format(int(c)))
        return int(hash_chars[:self.difficulty]) == 0

    def find_nonce(self):
        def generate_nonce(): return ''.join([random.choice(string.ascii_letters + string.digits) for i in range(10 * self.difficulty)])
        self.nonce = generate_nonce()
        while not self.good_nonce():
            # print(f'Bad nonce ({self.nonce}). Trying again...')
            self.nonce = generate_nonce()
        print(f'Good nonce ({self.nonce}).')
        return self.nonce


if __name__ == '__main__':
    private_key1, public_key1 = generate_keys()
    private_key2, public_key2 = generate_keys()
    private_key3, public_key3 = generate_keys()

    transaction1 = Transaction()
    transaction1.add_input(public_key1, 1)
    transaction1.add_output(public_key2, 1)
    transaction1.sign(private_key1)

    if transaction1.is_valid():
        print('Success, Transaction is valid:')
    else:
        print('ERROR, Transaction is NOT valid:')

    with open('data/public1.dat', 'wb') as address_fp:
        pickle.dump(public_key1, address_fp)

    with open('data/transaction.dat', 'wb') as address_fp:
        pickle.dump(transaction1, address_fp)

    with open('data/transaction.dat', 'rb') as address_fp:
        transaction_loaded = pickle.load(address_fp)

    if transaction_loaded.is_valid():
        print('Success, Loaded transaction is valid:')
    else:
        print('ERROR, Loaded transaction is NOT valid:')

    print('--------------- test transaction blocks --------------')

    root = TransactionBlock(None)
    root.addTransaction(transaction1)

    transaction2 = Transaction()
    transaction2.add_input(public_key2, 1.2)
    transaction2.add_output(public_key3, 1)
    transaction2.sign(private_key2)

    root.addTransaction(transaction2)

    B1 = TransactionBlock(root)

    transaction3 = Transaction()
    transaction3.add_input(public_key2, 2.2)
    transaction3.add_output(public_key3, 2)
    transaction3.sign(private_key2)

    transaction4 = Transaction()
    transaction4.add_input(public_key3, 1.2)
    transaction4.add_output(public_key1, 1)
    transaction4.add_required(public_key2)
    transaction4.sign(private_key3)
    transaction4.sign(private_key2)

    B1.addTransaction(transaction3)
    B1.addTransaction(transaction4)

    start = time.time()
    print(B1.find_nonce())
    elapsed_time = time.time() - start
    print('elapsed time:', str(elapsed_time) + 's')
    if elapsed_time < 60:
        print('ERROR! Mining is too fast!')
    if B1.good_nonce():
        print('Success, Nonce is good!')
    else:
        print('ERROR! Nonce is not good!')

    root.is_valid()
    B1.is_valid()

    with open('data/block_1.dat', 'wb') as block_1_fp:
        pickle.dump(B1, block_1_fp)

    with open('data/block_1.dat', 'rb') as load_block_1_fp:
        B1_loaded = pickle.load(load_block_1_fp)

    for block in [root, B1, B1_loaded, B1_loaded.previous_block]:
        if block.is_valid():
            print('Success, Block is valid!')
        else:
            print('ERROR, Block is NOT valid')

    if B1_loaded.good_nonce():
        print('Success, Nonce is good after save and load!')
    else:
        print('ERROR! Nonce bad after save and load')

    # tampered block after loading (add a valid transaction)
    B1_loaded.previous_block.addTransaction(transaction4)

    # invalid block - invalid transactions in block
    B2 = TransactionBlock(B1)
    transaction5 = Transaction()
    transaction5.add_input(public_key1, 1)
    transaction5.add_output(public_key2, 100)
    transaction5.sign(private_key1)
    B2.addTransaction(transaction5)

    for n, block in enumerate([B1_loaded, B2]):
        if block.is_valid():
            print(f'ERROR, invalid block verified!!!')
        else:
            print(f'Success, invalid block detected')

    # test mining rewards
    private_key4, public_key4 = generate_keys()
    B3 = TransactionBlock(B2)
    B3.addTransaction(transaction2)
    B3.addTransaction(transaction3)
    B3.addTransaction(transaction4)
    transaction6 = Transaction()
    transaction6.add_output(public_key4, REWARD)
    B3.addTransaction(transaction6)

    if B3.is_valid():
        print('Success, block reward succeeds')
    else:
        print('Error, block reward failed')

    B4 = TransactionBlock(B2)
    B4.addTransaction(transaction2)
    B4.addTransaction(transaction3)
    B4.addTransaction(transaction4)
    transaction7 = Transaction()
    transaction7.add_output(public_key4, REWARD + 0.6)
    B4.addTransaction(transaction7)

    if B4.is_valid():
        print('Success, transaction fees succeeds')
    else:
        print('Error, transaction fees failed')

    B5 = TransactionBlock(B2)
    B5.addTransaction(transaction2)
    B5.addTransaction(transaction3)
    B5.addTransaction(transaction4)
    transaction7 = Transaction()
    transaction7.add_output(public_key4, REWARD + 1.2)
    B5.addTransaction(transaction7)

    if not B5.is_valid():
        print('Success, greedy miner detected')
    else:
        print('Error, greedy miner NOT detected')
