from openai.types.chat import ChatCompletionMessageParam
from constants import (
    LLM_BASE_URL,
    LLM_MODEL,
    PROMPT_CHARACTER,
    EXIT_CHARACTERS,
    SYSTEM_PROMPT,
)
from openai import OpenAI
from transcripts import append
from datetime import datetime, UTC


def main():
    client = OpenAI(base_url=LLM_BASE_URL, api_key="ollama")
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
    ]
    session_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    converse(client, messages, session_id)


def agent(
    input: str,
    client: OpenAI,
    messages: list[ChatCompletionMessageParam],
    session_id: str,
):
    messages.append({"role": "user", "content": input})
    append(session_id, datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"), "user", input)
    reply = ""
    stream = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            reply += delta
    print()
    messages.append({"role": "assistant", "content": reply})
    append(session_id, datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"), "assistant", reply)


def converse(
    client: OpenAI, messages: list[ChatCompletionMessageParam], session_id: str
):
    """
    The entrypoint to everything conversing.
    """
    while True:
        try:
            line = input(PROMPT_CHARACTER + " ")
            if line.strip() in EXIT_CHARACTERS:
                break
            if not line.strip():
                continue
            agent(line, client, messages, session_id)
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == "__main__":
    main()
