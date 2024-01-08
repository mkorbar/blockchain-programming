from cryptography.hazmat.primitives import hashes


class CBlock:
    data = None
    previous_hash: bytes = None
    previous_block = None

    def __init__(self, data, previous_block):
        self.previous_block = previous_block
        self.data = data

        if previous_block is None:
            self.previous_hash = bytes(0000)
        else:
            self.previous_hash = previous_block.compute_hash()

    def compute_hash(self):
        sha256 = hashes.Hash(hashes.SHA256())
        sha256.update(bytes(str(self.data), 'utf-8'))
        sha256.update(bytes(str(self.previous_hash), 'utf-8'))
        return sha256.finalize()

    def is_valid(self):
        if self.previous_block is None:
            return True
        return self.previous_block.compute_hash() == self.previous_hash


class String_class:
    string = None

    def __init__(self, my_string):
        self.string = my_string

    def __repr__(self):
        return self.string


if __name__ == '__main__':
    root = CBlock(b'I am root', None)
    B1 = CBlock('I am a child of root', root)
    B2 = CBlock('I am another child of root, brother of B1', root)
    B3 = CBlock(12341, B2)
    B4 = CBlock(String_class('test String'), B3)
    B5 = CBlock('Top block', B4)

    for block in [B1, B2, B3, B4, B5]:
        if block.previous_block.compute_hash() == block.previous_hash:
            print(block, 'has a correct hash')
        else:
            print(block, 'does not have a valid hash')

