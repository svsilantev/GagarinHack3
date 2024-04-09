from pydantic_settings import BaseSettings


class Config(BaseSettings):
    dbuser: str
    dbpassword: str
    dbhost: str
    dbname: str
    dbport: int
    reset_db: bool
    logging_level: str
    postgres_initdb_args: str
    service_name: str

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.dbuser}:{self.dbpassword}@{self.dbhost}:{self.dbport}/{self.dbname}'


config = Config(_env_file='api.env', _env_file_encoding='utf-8')