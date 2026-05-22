import os
from pathlib import Path
from dotenv import load_dotenv


class Configuration:
    # Configurations for the Chat
    PROMPT_CHARACTER = ">>>"
    EXIT_CHARACTERS = {"/quit", "/exit"}

    # Relevant Paths
    PATH_TO_DATA_TRANSCRIPTS = Path(__file__).parent / "data" / "transcripts"
    PATH_TO_ENV_FILE = Path(__file__).parent / ".env"
    PATH_TO_SYSTEM_PROMPT = Path(__file__).parent / "prompts" / "system_prompt.md"

    def __init__(self) -> None:
        load_dotenv(self.PATH_TO_ENV_FILE)

        llm_base_url = os.getenv("LLM_BASE_URL")

        if not llm_base_url:
            raise ValueError(f"Required Environment Variable: LLM_BASE_URL is missing.")

        self.llm_base_url = llm_base_url

        llm_primary_model = os.getenv("PRIMARY_LLM_MODEL")

        if not llm_primary_model:
            raise ValueError(
                f"Required Environment Variable: PRIMARY_LLM_MODEL is missing."
            )

        self.llm_primary_model = llm_primary_model
        self.system_prompt = (
            self.PATH_TO_SYSTEM_PROMPT.read_text(encoding="utf-8")
            if self.PATH_TO_SYSTEM_PROMPT.exists()
            else ""
        )
