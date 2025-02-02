from typing import Dict, Optional
from PyPDF2 import PdfReader
from cryptography.hazmat.backends import default_backend
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import load_pem_x509_certificate
from models.signer import Signer
from endesive import pdf

def sign_document(document: bytes, signer: Signer):
    pass


def sign_pdf(
    input_file: bytes,
    signer: Signer,
    reason: str | None,
    location: str | None,
    signature_position=(470, 840, 570, 640),
):
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
        datau = input_file.encode("utf-8")
    else:
        datau = input_file

    if not input_file.startswith(b"%PDF-1."):
        raise ValueError("Invalid PDF file")
    ###

    if not reason:
        reason = f"Documento assinado por {signer.name}"

    date = datetime.now().strftime("D:%Y%m%d%H%M%S+00'00'")
    dct = {
        "aligned": 0,
        "sigflags": 3,
        "sigflagsft": 132,
        "sigpage": 0,
        "sigbutton": True,
        "sigfield": "Signature1",
        "auto_sigfield": True,
        "sigandcertify": True,
        "location": location,
        "reason": reason,
        "contact": signer.email,
        "signingdate": date,
        "type": "CERTIFICATION",
    }

    # Carrega a chave privada
    private_key = serialization.load_pem_private_key(
        signer.private_key, password=None, backend=default_backend()
    )

    # Carrega o certificado do Signer
    certificate = load_pem_x509_certificate(
        signer.certificate, backend=default_backend()
    )

    # Serializa a chave privada e o certificado no formato PKCS12
    pfx_data = pkcs12.serialize_key_and_certificates(
        name=signer.name.encode(),
        key=private_key,
        cert=certificate,
        cas=None,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Carrega a chave privada e o certificado do PKCS12
    key, cert, others = pkcs12.load_key_and_certificates(
        pfx_data, None, default_backend()
    )

    # Assina o documento utilizando o certificado e a chave privada
    datas = pdf.cms.sign(
        datau=datau,  # PDF data
        udct=dct,  # Signature properties
        key=key,  # Private key
        cert=cert,  # Certificate
        othercerts=others,  # Additional certificates
        algomd="sha256",  # Digest algorithm
        timestampurl=None,
    )

    return datau + datas


async def verify_document(
    document: bytes, trusted_signers: list
) -> Optional[Dict]:
    """
    Essa função recebe um documento PDF e uma lista de signatários confiáveis.
    Os signatários são apenas os existentes na base de dados da aplicação.
    Se o documento foi assinado por um signatário confiável, a função retorna
    os dados da assinatura.
    """
    from endesive import pdf
    from io import BytesIO

    print("Verifying document")
    pdf_bytes = BytesIO(document)
    # try:
    #     pdf_document = PdfReader(pdf_bytes)
    # except Exception as exc:
    #     print('Error reading PDF')
    #     print(exc)
    #     return False
    validated = False
    signatures = []
    verify_result = []
    trusted_cert_pems = [signer["certificate"] for signer in trusted_signers]
    trusted_signers = [signer["email"] for signer in trusted_signers]
    try:
        # Verifica a assinatura do documento
        verify_result = pdf.verify(document, trusted_cert_pems)
        for hashok, signatureok, certok in verify_result:
            # Verifica se foi assinado com um certificado confiável
            print(f"Signature: {signatureok}, Hash: {hashok}, Cert: {certok}")
            validated = signatureok and hashok and certok
    except Exception as exc:
        print('failed to verify')
        print(exc)
        return {
            "validated": validated,
            "signatures": None,
            "error": str(exc)
        }
    if validated:
        signatures = extract_signature(pdf_bytes)
        if not signatures or not isinstance(signatures, dict):
            validated = False
        else:
            if not signatures.get("name"):
                validated = False
            else:
                # Verifica se a assinatura foi feita por um signatário confiável
                for signer in trusted_signers:
                    if signer == signatures.get("name"):
                        validated = True
                        break
    else:
        return {
            "validated": False,
            "signatures": None
        }
    return {"validated": validated, "signatures": signatures}


def extract_signature(pdf_bytes: bytes):
    """
    Essa função tenta obter os dados da assinatura de um documento PDF.
    """
    try:
        if pdf_bytes:
            reader = PdfReader(pdf_bytes)

            root_obj = reader.trailer["/Root"].get_object()

            # Verificar se há um formulário AcroForm
            if "/AcroForm" not in root_obj:
                return "Nenhum formulário AcroForm encontrado."

            acroform_obj = root_obj["/AcroForm"].get_object()  # Resolver IndirectObject

            # Verificar se há campos
            if "/Fields" not in acroform_obj:
                return "Nenhum campo de assinatura encontrado."

            fields = acroform_obj["/Fields"]  # Lista de campos do PDF

            for field in fields:
                field_obj = field.get_object()  # Resolvendo o IndirectObject
                if field_obj.get("/FT") == "/Sig":  # Verifica se é uma assinatura
                    signature = field_obj.get("/V")  # Pega o valor da assinatura
                    if signature:
                        signature_obj = (
                            signature.get_object()
                            if isinstance(signature, type(field))
                            else signature
                        )

                        signature_data = {
                            "name": signature_obj.get("/Name", ""),
                            "reason": signature_obj.get("/Reason", ""),
                            "location": signature_obj.get("/Location", ""),
                            "data": signature_obj.get("/M", ""),
                        }
                        return signature_data
            return "Nenhuma assinatura encontrada."
        else:
            return "Arquivo PDF vazio"
    except Exception as e:
        return f"Erro ao extrair assinatura: {str(e)}"
