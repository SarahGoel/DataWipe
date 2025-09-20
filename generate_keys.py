#!/usr/bin/env python3
"""
Generate RSA key pair for digital signatures
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import os

def generate_rsa_keys():
    # Create keys directory if it doesn't exist
    os.makedirs("keys", exist_ok=True)
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Generate public key
    public_key = private_key.public_key()
    
    # Save private key
    with open("keys/private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save public key
    with open("keys/public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    print("RSA key pair generated successfully!")
    print("Private key: keys/private.pem")
    print("Public key: keys/public.pem")

if __name__ == "__main__":
    generate_rsa_keys()
