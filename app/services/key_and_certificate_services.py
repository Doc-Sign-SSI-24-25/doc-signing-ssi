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
    """
    Função que gera um par de chaves privada e pública RSA e retorna ambas as chaves em formato PEM.
    """
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


def generate_certificate(signer: Signer, not_valid_after: datetime = (datetime.now() + timedelta(days=365))) -> bytes:
    """
    Essa função recebe um objeto Signer e uma data opcional de validade do certificado.
    As chave privada e pública do utilizador são utilizadas para gerar um 
    certificado autoassinado, se o utilizador não tiver as chaves a função lança um ValueError.
    Se nenhuma data de validade for fornecida, o certificado será válido por 365 dias. 
    Essa função retorna o certificado já assinado em formato PEM, para
    manter a padronização com as funções anteriores. 
    """
    
    if not signer.private_key or not signer.public_key:
        raise ValueError("Chave privada ou pública não encontrada")
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, signer.name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IPB"),
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
        .not_valid_after(not_valid_after)
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
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    return cert_pem


def generate_key_and_certificate(user_name: str, certificate_validity: datetime = (datetime.now() + timedelta(days=365))) -> tuple[bytes, bytes, bytes]:
    """
    Função que gera as chaves privada e pública e, posteriormente o certificado autoassinado,
    retornando as chaves e o certificado em formato PEM.
    Essa função é adequada para novos utilizadores que não possuem chaves ou certificados,
    pois recebe o nome do utilizador e a validade do certificado como argumentos, 
    em vez de um objeto Signer. 
    Se nenhuma data de validade for fornecida, o certificado será válido por 365 dias.
    """
    # Gera uma chave privada RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    # Cria os atributos do subject e issuer com os mesmos valores
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, user_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "IPB"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "PT"),
        ]
    )

    # Gera certificado autoassinado com a chave pública gerada anteriormente
    # e os atributos do subject e issuer
    # e o assina com a chave privada
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(certificate_validity)
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256(), default_backend())
    )

    # Codifica as chave privadam pública e o Certificado no formato PEM
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