from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECURITY_KEY: str
    ALGORITHM: str
    SCHEMES_CRYPT: str
    API_KEY: str
    TEST_DB_HOST: str
    TEST_DB_PORT: str
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    @property
    def SYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"

    @property
    def secret_key_env(self):
        return self.SECURITY_KEY

    @property
    def algorithm_env(self):
        return self.ALGORITHM

    @property
    def schemes_env(self):
        return [self.SCHEMES_CRYPT]

    @property
    def API_KEY(self):
        return self.API_KEY

    class Config:
        env_file = ".env"

settings = Settings()