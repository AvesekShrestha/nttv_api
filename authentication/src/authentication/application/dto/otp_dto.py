from dataclasses import dataclass

@dataclass
class OTPResendDTO:
    email : str

@dataclass
class OTPVerifyDTO:
    email : str
    otp : str
