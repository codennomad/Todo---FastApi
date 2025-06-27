from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class loads environment variables from a .env file
    and provides them as attributes for easy access throughout
    the application.

    Attributes:
        DATABASE_URL (str): The URL for connecting to the database.
        SECRET_KEY (str): A secret key used for signing JWTs and other
        security purposes.
        ALGORITHM (str): The cryptographic algorithm used for JWTs
        (e.g., 'HS256').
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The duration in minutes for which
        an access token is valid.
    """
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()
