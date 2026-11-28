from typing import Any

from src.application.shared.email_sender_interface import (
    EmailSenderInterface,
)
from src.config.settings import settings
from src.infrastructure.messaging.kafka.events.auth.auth_event import (
    UserCreatedEvent,
)
from src.infrastructure.providers.smtp.smtp_email_sender import (
    SmtpEmailSender,
)
from src.infrastructure.messaging.kafka.handlers.auth.shared import (
    deliver_auth_email,
)


def build_message(event: UserCreatedEvent) -> str:
    return (
        "Welcome to the NTC Ticket Management System.\n\n"
        "Use this verification code to verify your account:\n\n"
        f"{event.data.otp.get_secret_value()}\n\n"
        "Do not share this code with anyone.\n\n"
        "If you did not request this account, you can ignore this email."
    )


async def handle(
    payload: dict[str, Any],
    *,
    email_sender: EmailSenderInterface | None = None,
) -> None:
    event = UserCreatedEvent.model_validate(payload)

    sender = (
        email_sender
        if email_sender is not None
        else SmtpEmailSender(settings=settings)
    )

    await deliver_auth_email(
        event_id=event.id,
        event_type=event.event_type,
        recipient=str(event.data.email),
        subject="Verify your NTC account",
        body=build_message(event),
        email_sender=sender,
    )
