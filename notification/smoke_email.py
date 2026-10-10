import asyncio

from src.config.settings import settings
from src.infrastructure.providers.smtp.smtp_email_sender import SmtpEmailSender

asyncio.run(SmtpEmailSender(settings).send("webkalpit@gmail.com", "Smoke test", "Hello from the notification service"))
