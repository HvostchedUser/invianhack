from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    server: str = "hack.invian.ru:9094"
    group_id: str = "yem"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="KAFKA_")

    def get_config(self) -> dict[str, str]:
        return {
            "bootstrap.servers": self.server,
            "group.id": self.group_id,
            "auto.offset.reset": "earliest",
        }


kafka_settings = KafkaSettings()
