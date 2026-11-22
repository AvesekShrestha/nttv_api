from src.application.exceptions.delivery_exception import (
    DeliveryError,
    PermanentDeliveryError,
)


class RecipientLookupError(DeliveryError):
    """Lookup failed and may succeed later."""


class RecipientNotFoundError(PermanentDeliveryError):
    """The requested recipient does not exist."""
