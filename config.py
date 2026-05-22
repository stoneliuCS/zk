import os
from pathlib import Path
from dotenv import load_dotenv


class Configuration:
    # Configurations for the Chat
    PROMPT_CHARACTER = ">"
    EXIT_CHARACTERS = {"/quit", "/exit"}
    ROOT_PATH = Path(__file__).parent

    # Relevant Paths
    PATH_TO_DATA_TRANSCRIPTS = ROOT_PATH / "data" / "transcripts"
    PATH_TO_ENV_FILE = ROOT_PATH / ".env"
    PATH_TO_SYSTEM_PROMPT = ROOT_PATH / "prompts" / "system_prompt.md"

    def _raise_required_env_error(self, missing_env_val: str):
        raise ValueError(
            f"Required Environment Variable: {missing_env_val} is missing."
        )

    def __init__(self) -> None:
        load_dotenv(self.PATH_TO_ENV_FILE)

        llm_base_url = os.getenv("LLM_BASE_URL")

        if not llm_base_url:
            self._raise_required_env_error("LLM_BASE_URL")

        self.llm_base_url = llm_base_url

        llm_primary_model = os.getenv("PRIMARY_LLM_MODEL")

        if not llm_primary_model:
            self._raise_required_env_error("PRIMARY_LLM_MODEL")

        self.llm_primary_model = llm_primary_model

        db_uri = os.getenv("DB_URI")

        if not db_uri:
            self._raise_required_env_error("DB_URI")
        self.db_uri = db_uri

        embed_model = os.getenv("EMBED_MODEL")
        if not embed_model:
            self._raise_required_env_error("EMBED_MODEL")
        self.embed_model = embed_model

        self.system_prompt = (
            self.PATH_TO_SYSTEM_PROMPT.read_text(encoding="utf-8")
            if self.PATH_TO_SYSTEM_PROMPT.exists()
            else ""
        )
        self.api_key = os.getenv("API_KEY") if os.getenv("API_KEY") else "ollama"
        self.debug = os.getenv("DEBUG") == "true" if os.getenv("DEBUG") else False
        self.location = os.getenv("LOCATION")
        self.username = os.getenv("USERNAME") if os.getenv("USERNAME") else "Anonymous"
