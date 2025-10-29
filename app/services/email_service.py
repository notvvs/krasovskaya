from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import NameEmail

from app.core.config import settings


class EmailClient:
    def __init__(self):
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD.get_secret_value(),  # SecretStr -> str
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_SERVER,
            MAIL_STARTTLS=settings.EMAIL_USE_TLS,  # Используем TLS (STARTTLS)
            MAIL_SSL_TLS=settings.EMAIL_USE_SSL,   # Используем SSL
            USE_CREDENTIALS=settings.EMAIL_USE_CREDS,  # Правильное название поля
            VALIDATE_CERTS=True
        )
        self.client = FastMail(conf)

    async def send_email(self, to_email: str, subject: str, body: str):
        message = MessageSchema(
            subject=subject,
            recipients=[NameEmail(name="", email=to_email)],
            body=body,
            subtype=MessageType.plain
        )
        await self.client.send_message(message)
