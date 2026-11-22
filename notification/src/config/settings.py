from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str = Field(validation_alias="DATABASE_URL")

    smtp_host: str = Field(validation_alias="EMAIL_HOST")
    smtp_port: int = Field(validation_alias="EMAIL_PORT")
    smtp_email: str = Field(validation_alias="EMAIL_HOST_USER")
    smtp_password: str = Field(validation_alias="EMAIL_HOST_PASSWORD")
    default_from_email: str = Field(validation_alias="DEFAULT_FROM_EMAIL")
    email_use_tls: bool = Field(validation_alias="EMAIL_USE_TLS")
    kafka_bootstrap_servers: str = Field(validation_alias="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: str = Field(validation_alias="KAFKA_GROUP_ID")
    kafka_ticket_topic: str = Field(validation_alias="KAFKA_TICKET_TOPIC")
    kafka_ticket_dlq_topic: str = "ticket.events.dlq"
    kafka_auth_topic: str = "auth.events"
    kafka_auth_dlq_topic: str = "auth.events.dlq"
    kafka_max_retries: int = 3
    kafka_retry_delay_seconds: float = 5.0
    delivery_worker_interval: int = 60
    ticket_service_url: str = Field(
        validation_alias="TICKET_SERVICE_URL",
    )
    ticket_api_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        validation_alias="TICKET_API_TIMEOUT_SECONDS",
    )
    authentication_service_url: str = Field(
        validation_alias="AUTHENTICATION_SERVICE_URL",
    )

    authentication_api_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        validation_alias="AUTHENTICATION_API_TIMEOUT_SECONDS",
    )

    delivery_worker_email: str = Field(
        default="",
        alias="DELIVERY_WORKER_EMAIL",
    )
    
    delivery_worker_password: SecretStr = Field(
        default=SecretStr(""),
        alias="DELIVERY_WORKER_PASSWORD",
    )

    cors_allowed_origins: list[str] = Field(
    default_factory=lambda: ["http://localhost:5173"],
    validation_alias="CORS_ALLOWED_ORIGINS",
    )


settings = Settings() # type: ignore[call-arg]
