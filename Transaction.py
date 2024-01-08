import Signatures
from cryptography.hazmat.primitives.serialization import Encoding


class Transaction:
    inputs = None
    outputs = None
    signatures = None
    required = None

    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.signatures = []
        self.required = []

    def add_input(self, from_address, amount):
        self.inputs.append((from_address, amount))

    def add_output(self, to_address, amount):
        self.outputs.append((to_address, amount))

    def add_required(self, address):
        self.required.append(address)

    def sign(self, private_key):
        message = self.__gather()
        signature = Signatures.sign(message, private_key)
        self.signatures.append(signature)

    def __gather(self):
        return [self.inputs, self.outputs, self.required]

    def is_valid(self):
        message = self.__gather()
        # outputs must not be greater than inputs
        # outputs and inputs should not be negative
        in_amount = 0
        out_amount = 0
        for addr, amount in self.inputs:
            if amount < 0:
                return False
            in_amount += amount
        for addr, amount in self.outputs:
            if amount < 0:
                return False
            out_amount += amount
        # if out_amount > in_amount:
        #    return False

        # all inputs must be signed
        for from_address, amount in self.inputs:
            found = False
            for signature in self.signatures:
                if Signatures.verify(message, signature, from_address):
                    found = True
                    break
            if not found:
                return False

        # all required must be signed
        for arbiter_addr in self.required:
            found = False
            for signature in self.signatures:
                if Signatures.verify(message, signature, arbiter_addr):
                    found = True
                    break
            if not found:
                return False

        return True

    def __repr__(self):
        inputs = [f'{amount} from {addr}' for addr, amount in self.inputs]
        outputs = [f'{amount} to {addr}' for addr, amount in self.outputs]
        required = [f'required {addr}' for addr in self.required]
        signatures = [f'signedBy {addr}' for addr in self.signatures]
        return f"({inputs} ->({required})-> {outputs})({signatures})"

    def __str__(self):
        inputs = [f'{str(addr)[-34:-26]}[{amount}]' for addr, amount in self.inputs]
        outputs = [f'{str(addr)[-34:-26]}[{amount}]' for addr, amount in self.outputs]
        required = [f're{str(addr)[-34:-26]}' for addr in self.required]
        signatures = [f'signedBy {str(addr)[-34:-26]}' for addr in self.signatures]
        return f"({','.join(inputs)}->({','.join(required)})-> {','.join(outputs)})"


if __name__ == '__main__':
    private_key1, public_key1 = Signatures.generate_keys()
    private_key2, public_key2 = Signatures.generate_keys()
    private_key3, public_key3 = Signatures.generate_keys()
    private_key4, public_key4 = Signatures.generate_keys()

    # first test case
    transaction1 = Transaction()
    transaction1.add_input(public_key1, 1)
    transaction1.add_output(public_key2, 1)
    transaction1.sign(private_key1)

    # second test case - transaction to a multiple accounts
    transaction2 = Transaction()
    transaction2.add_input(public_key1, 2)
    transaction2.add_output(public_key2, 1)
    transaction2.add_output(public_key3, 1)
    transaction2.sign(private_key1)

    # third transaction - escrow transaction
    transaction3 = Transaction()
    transaction3.add_input(public_key1, 1.2)
    transaction3.add_output(public_key2, 1.1)
    transaction3.add_required(public_key3)
    transaction3.sign(private_key1)
    transaction3.sign(private_key3)

    # check for validity on valid transactions
    for t in [transaction1, transaction2, transaction3]:
        if t.is_valid():
            print("Successfully signed transaction", transaction1)
        else:
            print(f"ERROR! Transaction {transaction1} is not signed properly")

    # invalid transaction - not signed by sender
    transaction4 = Transaction()
    transaction4.add_input(public_key3, 1)
    transaction4.add_output(public_key2, 1)
    transaction4.sign(private_key2)

    # invalid transaction - escrow transaction not signed by arbiter
    transaction5 = Transaction()
    transaction5.add_input(public_key1, 1.2)
    transaction5.add_output(public_key2, 1.1)
    transaction5.add_required(public_key3)
    transaction5.sign(private_key1)

    # invalid transaction - two input addressed, signed by only one
    transaction6 = Transaction()
    transaction6.add_input(public_key1, 1.2)
    transaction6.add_input(public_key3, 1)
    transaction6.add_output(public_key2, 2.2)
    transaction6.sign(private_key1)

    # invalid transaction - outputs exceeds the inputs
    transaction7 = Transaction()
    transaction7.add_input(public_key1, 1.2)
    transaction7.add_output(public_key2, 3.2)
    transaction7.add_output(public_key3, 3.2)
    transaction7.sign(private_key1)

    # invalid transaction - amount is negative
    transaction8 = Transaction()
    transaction8.add_input(public_key1, -1.2)
    transaction8.add_output(public_key2, -1.2)
    transaction8.sign(private_key1)

    # tampered valid transaction
    transaction9 = Transaction()
    transaction9.add_input(public_key1, 1)
    transaction9.add_output(public_key2, 1)
    transaction9.sign(private_key1)
    transaction9.outputs[0] = (public_key3, 1)

    # check for validity on invalid transactions
    for t in [transaction4, transaction5, transaction6, transaction7, transaction8, transaction9]:
        if t.is_valid():
            print(f"ERROR! Invalid transaction {transaction4} passed as valid")
        else:
            print(f"Successfully flagged {transaction1} as invalid.")
