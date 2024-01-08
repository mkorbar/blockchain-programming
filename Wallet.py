import Socket_Client
import Socket_Server
import Transaction
import Signatures

private_key1, public_key1 = Signatures.generate_keys()
private_key2, public_key2 = Signatures.generate_keys()
private_key3, public_key3 = Signatures.generate_keys()

transaction1 = Transaction.Transaction()
transaction1.add_input(public_key1, 4.0)
transaction1.add_input(public_key2, 1.0)
transaction1.add_output(public_key3, 4.8)
transaction1.sign(private_key1)
transaction1.sign(private_key2)

####

transaction2 = Transaction.Transaction()
transaction2.add_input(public_key3, 4.0)
transaction2.add_output(public_key2, 4.0)
transaction2.add_required(public_key1)

transaction2.sign(private_key3)
transaction2.sign(private_key1)

# send transactions
ip = 'localhost'
Socket_Client.send_object(ip, transaction1)
print(f'transaction sent to: {ip}')
Socket_Client.send_object(ip, transaction2)
print(f'transaction sent to: {ip}')


# listen for response
socket_server = Socket_Server.new_connection('localhost', 5000)
while True:
    new_block = Socket_Server.receive_object(socket_server)
    if new_block is not None:
        print('Received new block: ', new_block)
        break
socket_server.close()

if new_block is not None and new_block.is_valid():
    print('Success! Block is valid')
    if new_block.good_nonce():
        print('Success! Nonce is valid')
        for transaction in new_block.data:
            if transaction == transaction1:
                print('Success! Transaction1 is present')
            if transaction == transaction2:
                print('Success! Transaction2 is present')

# add the block to the blockchain

head_blocks = [None]
for b in head_blocks:
    if b is not None and new_block.previous_hash == b.compute_hash():
        new_block.previous_block = b
        head_blocks.remove()
        head_blocks.append(new_block)
