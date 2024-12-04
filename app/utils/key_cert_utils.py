from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.x509.base import Certificate
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from app.models.signer import Signer

from cryptography.hazmat.backends import default_backend


def generate_key_pair():
    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    # Serializa a chave privada no formato PEM
    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    # Serializa a chave pública no formato PEM
    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_pem, public_pem


"""
Gera um certificado autoassinado, se o utilizador já tiver uma chave privada
"""


def generate_cert(signer: Signer) -> Certificate:
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, signer.name),
            # x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Organization"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(
            serialization.load_pem_public_key(signer.public_key, default_backend())
        )
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(datetime.now() + timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(
            serialization.load_pem_private_key(
                signer.private_key, password=None, backend=default_backend()
            ),
            hashes.SHA256(),
            default_backend(),
        )
    )
    return cert


def generate_key_and_cert(common_name):
    # Gera chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    # Cria os atributos do certificado
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            # x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Organization"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
        ]
    )

    # Gera certificado autoassinado
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(datetime.now() + timedelta(days=365))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    # Retorna a chave privada e o certificado em formato PEM
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)

    return private_key_pem, public_key_pem, cert_pem
