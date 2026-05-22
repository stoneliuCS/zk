from openai.types.chat import ChatCompletionMessageParam
from config import Configuration
from openai import OpenAI
from transcripts import append
from datetime import datetime, UTC


def main():
    config = Configuration()
    client = OpenAI(base_url=config.LLM_BASE_URL, api_key="ollama")
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": config.SYSTEM_PROMPT,
        },
    ]
    session_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    converse(client, messages, session_id, config)


def agent(
    input: str,
    client: OpenAI,
    messages: list[ChatCompletionMessageParam],
    session_id: str,
    config: Configuration,
):
    messages.append({"role": "user", "content": input})
    append(
        session_id, datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"), "user", input, config
    )
    reply = ""
    stream = client.chat.completions.create(
        model=config.LLM_MODEL,
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
    append(
        session_id,
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
        "assistant",
        reply,
        config,
    )


def converse(
    client: OpenAI,
    messages: list[ChatCompletionMessageParam],
    session_id: str,
    config: Configuration,
):
    """
    The entrypoint to everything conversing.
    """
    while True:
        try:
            line = input(config.PROMPT_CHARACTER + " ")
            if line.strip() in config.EXIT_CHARACTERS:
                break
            if not line.strip():
                continue
            agent(line, client, messages, session_id, config)
        except (EOFError, KeyboardInterrupt):
            print()
            break


if __name__ == "__main__":
    main()
