from cryptography.hazmat.backends import default_backend
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import load_pem_x509_certificate
from app.models.signer import Signer
from endesive import pdf

def sign_document(document:bytes, signer: Signer):
    pass

def sign_pdf(input_file:bytes, signer: Signer, reason : str | None,location : str | None ,signature_position = (470, 840, 570, 640)):
    """
    Função para assinar um documento PDF com um certificado digital.
    Recebe um objeto Signer com a chave privada e o certificado do Signer,
    o documento a ser assinado, a razão da assinatura e a localização da assinatura.
    O atributo signature_position é uma tupla com as coordenadas da assinatura no documento para
    implementações futuras.
    Retorna o documento assinado em bytes.
    """
    
    # Verifica se o Signer tem uma chave privada e um certificado
    if not signer.private_key or not signer.certificate:
        raise ValueError("Signer must have a private key and a certificate")
    
    ### Verificações do formato do documento
    if isinstance(input_file, str):
        datau = input_file.encode('utf-8')
    else:
        datau = input_file
    
    if not input_file.startswith(b'%PDF-1.'):
        raise ValueError("Invalid PDF file")
    ###
        
        
    if not reason:
        reason = f'Documento assinado por {signer.name}'
        
    date = datetime.now().strftime("D:%Y%m%d%H%M%S+00'00'")
    dct = {
        'aligned': 0,
        'sigflags': 3,
        'sigflagsft': 132,
        'sigpage': 0,
        'sigbutton': True,
        'sigfield': 'Signature1',
        'auto_sigfield': True,
        'sigandcertify': True,
        'location': location,
        'reason': reason,
        'contact': signer.email,
        'signingdate': date,
        'type': 'CERTIFICATION'
    }
    
    # Carrega a chave privada
    private_key = serialization.load_pem_private_key(
        signer.private_key,
        password=None,
        backend=default_backend()
    )
    
    # Carrega o certificado do Signer
    certificate = load_pem_x509_certificate(
        signer.certificate,
        backend=default_backend()
    )
    
    # Serializa a chave privada e o certificado no formato PKCS12
    pfx_data = pkcs12.serialize_key_and_certificates(
        name=signer.name.encode(),
        key=private_key,
        cert=certificate,
        cas=None,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Carrega a chave privada e o certificado do PKCS12
    key,cert,others = pkcs12.load_key_and_certificates(
        pfx_data,
        None,
        default_backend()
    )
    
    # Assina o documento utilizando o certificado e a chave privada
    datas = pdf.cms.sign(
        datau=datau,              # PDF data
        udct=dct,                # Signature properties
        key=key,                # Private key  
        cert=cert,               # Certificate
        othercerts=others,             # Additional certificates
        algomd='sha256',          # Digest algorithm
        timestampurl=None,
    )
    
    return datau+datas

def verify_document(document:bytes):
    pass