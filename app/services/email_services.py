import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path


async def send_email(
    sender_email: str,
    sender_name: str,
    recipient_email: str,
    subject: str,
    message: str,
    attachment_filename: str | None,
    attachment_content: bytes | None,
):
    """
    Serviço para enviar e-mails usando Gmail SMTP.
    """
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "seu_email@gmail.com"
    smtp_password = "sua_senha_de_aplicativo"

    # Configuração do e-mail
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    # Anexar arquivo, se fornecido
    if attachment_content and attachment_filename:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment_content)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={Path(attachment_filename).name}",
        )
        msg.attach(part)

    # Enviar e-mail via Gmail SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return {"message": "E-mail enviado com sucesso!"}
    except Exception as e:
        raise Exception(f"Erro ao enviar e-mail: {str(e)}")
