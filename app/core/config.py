from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
	DATABASE_URL: str = Field(
		default="postgresql+psycopg://oms_user:oms_pass@postgres:5432/oms_db"
	)
	TIMEZONE: str = Field(default="Asia/Kolkata")
	CURRENCY: str = Field(default="INR")
	PAYMENT_GATEWAY_BASE_URL: str = Field(default="http://payment-gateway:9000")

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"


settings = Settings()
