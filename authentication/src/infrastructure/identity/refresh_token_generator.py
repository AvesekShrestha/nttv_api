import secrets
from src.application.shared.refresh_token_generator_interface import IRefreshTokenGenerator

class RefreshTokenGenerator(IRefreshTokenGenerator):

    def generate(self, refresh_token_id : str) -> str:
        return f"{refresh_token_id}.{secrets.token_urlsafe(32)}"
