import secrets
from authentication.application.shared.otp_generator_interface import IOTPGenerator

class OTPGenerator(IOTPGenerator) : 
    def generate(self) -> str : 
        return f"{secrets.randbelow(1_000_000):06d}"
