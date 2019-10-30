from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import click
from flask import current_app
from flask.cli import with_appcontext


def public_key_to_bytes(key):
    """Convert the given private key into bytes"""
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def init_keys(keys_folder: str):
    """Generate and store both public and private keys in
    the given folder in file 'keys.cfg'"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=512,  # 512 bits
        backend=default_backend()
    )
    public_key = private_key.public_key()

    # Writing private key
    with open('%s/private_key.pem' % keys_folder, 'wb') as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Writing public key
    with open('%s/public_key.pem' % keys_folder, 'wb') as f:
        f.write(
            public_key_to_bytes(public_key)
        )


def load_keys(keys_folder: str):
    """Load the keys from the .pem files in the given keys_folder"""
    # Reading private key
    with open('%s/private_key.pem' % keys_folder, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

    # Reading public key
    with open('%s/public_key.pem' % keys_folder, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )

    return (private_key, public_key)


@click.command('gen-keys')
@with_appcontext
def gen_new_keys():
    """Clear the existing keys and generate new ones."""
    init_keys(current_app.instance_path)
    click.echo('Generated new server\'s keys.')


def init_app(app):
    app.cli.add_command(gen_new_keys)