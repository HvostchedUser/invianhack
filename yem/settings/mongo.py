from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import MongoDsn


class MongoSettings(BaseSettings):
    uri: MongoDsn = "mongodb://localhost:27017"
    db_name: str = "vehicle_tracking"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MONGO_")


mongo_settings = MongoSettings()
