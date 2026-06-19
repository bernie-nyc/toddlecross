import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keys():
    base_dir = Path(__file__).resolve().parent.parent
    keys_dir = base_dir / 'config' / 'lti_keys'
    keys_dir.mkdir(parents=True, exist_ok=True)
    
    private_key_path = keys_dir / 'private.key'
    public_key_path = keys_dir / 'public.key'
    
    if not private_key_path.exists() or not public_key_path.exists():
        print("Generating new RSA 2048 key pair...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Serialize Private Key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize Public Key
        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(private_key_path, 'wb') as f:
            f.write(pem_private)
            
        with open(public_key_path, 'wb') as f:
            f.write(pem_public)
        print(f"Keys generated and saved in {keys_dir}")
    else:
        print("LTI keys already exist. Skipping generation.")

if __name__ == '__main__':
    generate_keys()
