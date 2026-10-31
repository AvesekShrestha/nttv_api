import asyncio
import logging
import smtplib
from email.message import EmailMessage

from src.application.exceptions.delivery_exception import (
    DeliveryError,
    PermanentDeliveryError,
)
from src.application.shared.email_sender_interface import EmailSenderInterface
from src.config.settings import Settings

logger = logging.getLogger(__name__)


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
                self._settings.smtp_host,
                self._settings.smtp_port,
                timeout=10,
            ) as smtp:
                smtp.starttls()
                smtp.login(
                    self._settings.smtp_email,
                    self._settings.smtp_password,
                )
                smtp.send_message(message)

        except smtplib.SMTPRecipientsRefused as exc:
            # Every recipient was rejected. Treat permanent SMTP
            # 5xx rejections as non-retryable.
            codes = [code for code, _ in exc.recipients.values()]
        
            if codes and all(500 <= code < 600 for code in codes):
                raise PermanentDeliveryError(
                    "SMTP permanently rejected recipient"
                ) from exc
        
            raise DeliveryError(
                "SMTP temporarily rejected recipient"
            ) from exc
        
        except smtplib.SMTPException as exc:
            raise DeliveryError("SMTP delivery failed") from exc
        
        except OSError as exc:
            raise DeliveryError("SMTP connection failed") from exc
        
