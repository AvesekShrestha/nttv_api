import jwt

from src.application.shared.jwt_generator_interface import IJWTGenerator
from src.application.shared.jwt_payload import JWTPayload
from src.application.exceptions.access_token_exception import InvalidAccessToken, ExpiredAccessToken

from src.config import settings

class JWTGenerator(IJWTGenerator):

    async def generate(self, payload: JWTPayload) -> str:
        return jwt.encode(
            payload.model_dump(),
            settings.JWT_SECRET_KEY,
            algorithm="HS256",
        )

    async def verify(self, token: str) -> JWTPayload:
        try:
            decoded = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"],
            )

            return JWTPayload.model_validate(decoded)

        except jwt.ExpiredSignatureError as exc:
            raise ExpiredAccessToken(
                "Access token has expired"
            ) from exc

        except jwt.InvalidTokenError as exc:
            print(
                "JWT ERROR:",
                type(exc).__name__,
                repr(str(exc)),
            )

            raise InvalidAccessToken(
                "Invalid access token"
            ) from exc
