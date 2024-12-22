from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from pathlib import Path
from fastapi import HTTPException, UploadFile
from bson import ObjectId
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()



class EmailController:
    def __init__(self, db):
        self.db = db

    async def send_email(self, user_id: str, subject: str, message: str, emails: list[str], attachment: UploadFile | None = None,):
        """
        Envia um e-mail utilizando os dados do usuário logado.

        Args:
            user_id (str): ID do usuário logado.
            subject (str): Assunto do e-mail.
            message (str): Mensagem do e-mail.
            emails (list[str]): Lista de destinatários.
            attachment (UploadFile | None): Arquivo opcional para anexar ao e-mail.

        Returns:
            dict: Informações sobre o status do envio.
        """
        # Buscar informações do usuário logado no banco de dados
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        sender_name = user["name"]
        sender_email = user["email"]

        try:
            # Configurar servidor SMTP (Gmail)
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')

            # Criar a mensagem do e-mail
            msg = MIMEMultipart()
            msg["From"] = f"{sender_name} <{sender_email}>"
            msg["To"] = ", ".join(emails)
            msg["Subject"] = subject

            # Adicionar corpo do e-mail
            msg.attach(MIMEText(message, "plain"))

            # Adicionar anexo, se fornecido
            if attachment:
                file_content = await attachment.read()
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_content)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={Path(attachment.filename).name}",
                )
                msg.attach(part)

            # Enviar o e-mail
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, emails, msg.as_string())
            server.quit()

            return {"message": "E-mail enviado com sucesso!"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")
