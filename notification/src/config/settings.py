from pydantic import Field
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
    kafka_max_retries: int = 3
    kafka_retry_delay_seconds: float = 5.0
    delivery_worker_interval: int = 60


settings = Settings() # type: ignore[call-arg]
