from constants import PATH_TO_DATA_TRANSCRIPTS
import json


def append(session_id: str, time_stamp: str, role: str, content: str) -> None:
    PATH_TO_DATA_TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    path = PATH_TO_DATA_TRANSCRIPTS / f"{session_id}.jsonl"
    line = json.dumps({"time_stamp": time_stamp, "role": role, "content": content})
    with path.open("a") as f:
        f.write(line + "\n")
