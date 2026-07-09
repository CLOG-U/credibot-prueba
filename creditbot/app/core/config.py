from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "CrediBot"
    app_env: str = "development"
    app_debug: bool = True

    supabase_url: str = ""
    supabase_service_role_key: str = ""

    whatsapp_verify_token: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_api_version: str = "v20.0"

    default_country_code: str = "593"


settings = Settings()
