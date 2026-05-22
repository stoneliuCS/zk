from datetime import datetime, UTC
from pathlib import Path
from dotenv import load_dotenv


class Configuration:
    PROMPT_CHARACTER = ">>>"

    EXIT_CHARACTERS = {"/quit", "/exit"}

    LLM_BASE_URL = "http://localhost:11434/v1"

    LLM_MODEL = "qwen2.5:7b"

    SYSTEM_PROMPT = f"""You are ZK. You are Stone's Personal Assistant acting as a natural language ZettelKasten or a database for his life. You will accumulate knowledge on Stone's day to day life and look up information, constantly discarding and updating information into a database. When this chat was initated the current time is {datetime.now(UTC).isoformat(timespec="seconds")}. Be brief and conversational, do not spit out bullet points unless you are instructed to do so.
    """

    PATH_TO_DATA_TRANSCRIPTS = Path(__file__).parent / "data" / "transcripts"
    PATH_TO_ENV_FILE = Path(__file__).parent / ".env"

    def __init__(self) -> None:
        load_dotenv(self.PATH_TO_ENV_FILE)
