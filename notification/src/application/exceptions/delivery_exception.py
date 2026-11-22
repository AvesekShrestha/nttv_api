class DeliveryError(Exception):
    pass


class PermanentDeliveryError(DeliveryError):
    pass


class DeliveryClaimLostError(RuntimeError):
    """The job was recovered or claimed by another worker."""
