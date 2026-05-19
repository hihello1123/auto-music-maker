from dotenv import load_dotenv
import os

load_dotenv()

HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "12000"))
RELOAD: bool = os.getenv("RELOAD", "false").lower() == "true"

import json
CORS_ORIGINS: list[str] = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))

OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:30b")
OLLAMA_TIMEOUT_RAW: str = os.getenv("OLLAMA_TIMEOUT", "120")
OLLAMA_TIMEOUT: float | None = None if OLLAMA_TIMEOUT_RAW.strip() in {"", "0", "none", "None"} else float(OLLAMA_TIMEOUT_RAW)

ACE_STEP_CMD_TEMPLATE: str = os.getenv("ACE_STEP_CMD_TEMPLATE", "")
ACE_STEP_TIMEOUT: float = float(os.getenv("ACE_STEP_TIMEOUT", "3600"))
ACE_STEP_API_URL: str = os.getenv("ACE_STEP_API_URL", "")
ACE_STEP_API_KEY: str = os.getenv("ACE_STEP_API_KEY", "")
ACE_STEP_API_MODEL: str = os.getenv("ACE_STEP_API_MODEL", "")
ACE_STEP_API_POLL_INTERVAL: float = float(os.getenv("ACE_STEP_API_POLL_INTERVAL", "5"))
