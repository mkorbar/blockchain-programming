from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def generate_keys():
    private_key: RSAPrivateKey = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key: RSAPublicKey = private_key.public_key()

    public_serialised = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_key, public_serialised


def sign(message, private_key:RSAPrivateKey):
    message = bytes(str(message), 'utf-8')
    sign = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256()
    )
    return sign


def verify(message, signature: bytes, public_key: bytes):
    message = bytes(str(message), 'utf-8')
    public_key = serialization.load_pem_public_key(public_key)
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


if __name__ == '__main__':
    private_key, public_key = generate_keys()
    message = 'Hello secret World'
    signature = sign(message, private_key)

    correct = verify(message, signature, public_key)

    if correct:
        print('Signature verified, good signature')
    else:
        print('Bad Signature is bad')


    attacker_private, attacker_public = generate_keys()
    attacker_signature = sign(message, attacker_private)

    attacker_verify = verify(message, attacker_signature, public_key)
    if attacker_verify:
        print('Error, attacker signature checks out')
    else:
        print('Success, attacker signature detected')


    forged_message = verify('Hello forged World', signature, public_key)
    if forged_message:
        print('Error, forged signature checks out')
    else:
        print('Success, forged signature detected')
