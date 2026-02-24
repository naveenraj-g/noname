from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    FHIR_DATABASE_URL: str
    REDIS_URL: str
    KEYCLOAK_URL: str
    KEYCLOAK_REALM_NAME: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_DISCOVERY_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
