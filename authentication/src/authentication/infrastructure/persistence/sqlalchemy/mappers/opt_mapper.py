from authentication.domain.otp.otp_aggregate import OTPAggregate
from authentication.infrastructure.persistence.sqlalchemy.models.opt_model import OTP



class OTPMapper:

    @staticmethod
    def to_model(otp: OTPAggregate) -> OTP:
        return OTP(
            id=otp.id,
            email=otp.email,
            otp_hash=otp.otp_hash,
            expires_at=otp.expires_at,
            attempts=otp.attempts,
            max_attempts=otp.max_attempts,
            consumed_at=otp.consumed_at,
            created_at=otp.created_at,
            last_sent_at=otp.last_sent_at,
        )

    @staticmethod
    def to_domain(model: OTP) -> OTPAggregate:
        return OTPAggregate(
            _id=model.id,
            _email=model.email,
            _otp_hash=model.otp_hash,
            _expires_at=model.expires_at,
            _attempts=model.attempts,
            _max_attempts=model.max_attempts,
            _consumed_at=model.consumed_at,
            _created_at=model.created_at,
            _last_sent_at=model.last_sent_at,
        )
