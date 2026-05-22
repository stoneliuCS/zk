"""
Responsible for interfacing with the actual module client.
"""

from typing import Literal
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from config import Configuration
from zk.transcripts import append
from datetime import datetime, UTC


class ZK:
    def __init__(self, config: Configuration) -> None:
        self._config = config
        self._client = OpenAI(
            base_url=self._config.llm_base_url, api_key=self._config.api_key
        )
        self._messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self._config.system_prompt,
            },
        ]
        self._session = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    def _log_chat(
        self, role: Literal["user", "assistant"], response: str, timestamp: str
    ):
        append(
            self._session,
            timestamp,
            role,
            response,
            self._config,
        )

    def chat(self, prompt: str, context: str | None) -> tuple[str, str, str]:
        """
        Chats with the ZK Model. Returns the prompt of the user, the response by ZK, and the timestamp.
        """
        self._messages.append({"role": "user", "content": prompt})
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self._log_chat("user", prompt, timestamp)
        reply = ""

        to_send = list(self._messages)

        if context:
            to_send.insert(1, {"role": "system", "content": context})

        stream = self._client.chat.completions.create(
            model=self._config.llm_primary_model,
            messages=to_send,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if not delta:
                continue
            print(delta, end="", flush=True)
            reply += delta
        print()
        self._messages.append({"role": "assistant", "content": reply})
        self._log_chat("assistant", reply, timestamp)
        return (prompt, reply, timestamp)

    def embed(self, text: str):
        res = self._client.embeddings.create(input=text, model=self._config.embed_model)
        return res.data[0].embedding

    def get_current_session(self) -> str:
        return self._session
