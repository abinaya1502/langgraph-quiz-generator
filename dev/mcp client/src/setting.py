from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    db_port: str
    db_host: str
    db_name: str
    db_username: str
    db_password: str
    port: int
    host: str
    log_level: str
    @property
    def DB_URI(self):
        return (
        f"postgresql://{self.db_username}:"
        f"{self.db_password}@"
        f"{self.db_host}:"
        f"{self.db_port}/"
        f"{self.db_name}"
)

def get_config():
    return Config(
        db_port=os.getenv('DB_PORT', '5432'),
        db_host=os.getenv('DB_HOST', 'localhost'),
        db_name=os.getenv('DB_NAME', 'agent_as_tool_db'),
        db_username=os.getenv('DB_USERNAME', 'postgres'),
        db_password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('PORT', '8080')),
        host=os.getenv('HOST', '0.0.0.0'),
        log_level=os.getenv('LOG_LEVEL', 'INFO')
    )


config = get_config()
config_db = config.DB_URI