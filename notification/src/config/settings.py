from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )

    smtp_host: str = Field(
        default="smtp.gmail.com",
        validation_alias="EMAIL_HOST",
    )
    smtp_port: int = Field(
        default=587,
        validation_alias="EMAIL_PORT",
    )
    smtp_email: str = Field(
        ...,
        validation_alias="EMAIL_HOST_USER",
    )
    smtp_password: str = Field(
        ...,
        validation_alias="EMAIL_HOST_PASSWORD",
    )
    default_from_email: str = Field(
        ...,
        validation_alias="DEFAULT_FROM_EMAIL",
    )
    email_use_tls: bool = Field(
        default=True,
        validation_alias="EMAIL_USE_TLS",
    )


settings = Settings()  # type: ignore[call-arg]
