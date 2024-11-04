from pydantic_settings import BaseSettings

from dotenv import load_dotenv


from dotenv import load_dotenv
load_dotenv()





class Settings(BaseSettings):
    DB_HOST: str
    DB_NAME: str
    DB_PASS: str
    DB_PORT: int
    DB_USER: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    SECRET_KEY: str
    ALGORITHM: str


    @property
    def DB_URL(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()