import json

from config import Configuration


def append(
    session_id: str, time_stamp: str, role: str, content: str, config: Configuration
) -> None:
    config.PATH_TO_DATA_TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    path = config.PATH_TO_DATA_TRANSCRIPTS / f"{session_id}.jsonl"
    line = json.dumps({"time_stamp": time_stamp, "role": role, "content": content})
    with path.open("a") as f:
        f.write(line + "\n")
