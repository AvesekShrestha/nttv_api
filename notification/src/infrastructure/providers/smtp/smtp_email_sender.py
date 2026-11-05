import asyncio
import smtplib
from email.message import EmailMessage

from src.application.exceptions.delivery_exception import DeliveryError
from src.application.shared.email_sender_interface import EmailSenderInterface
from src.config.settings import Settings


class SmtpEmailSender(EmailSenderInterface):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send(self, to: str, subject: str, body: str) -> None:
        await asyncio.to_thread(self._send_sync, to, subject, body)

    def _send_sync(self, to: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self._settings.smtp_email
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(
                self._settings.smtp_host, self._settings.smtp_port, timeout=10
            ) as smtp:
                smtp.starttls()
                smtp.login(self._settings.smtp_email, self._settings.smtp_password)
                smtp.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:
            raise DeliveryError(str(exc)) from exc
