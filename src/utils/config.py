import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    google_api_key: str
    model: str
    max_iterations: int
    memory_limit: int
    log_level: str
    log_file: str

    @classmethod
    def load(cls):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        return cls(
            google_api_key=api_key,
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "8")),
            memory_limit=int(os.getenv("AGENT_MEMORY_LIMIT", "40")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=os.getenv("LOG_FILE", "logs/agent.log"),
        )