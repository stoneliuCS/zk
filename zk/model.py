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

    def _log_chat(self, role: Literal["user", "assistant"], response: str):
        append(
            self._session,
            datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            role,
            response,
            self._config,
        )

    def chat(self, prompt: str):
        """
        Chats with the ZK Model
        """
        self._messages.append({"role": "user", "content": prompt})
        self._log_chat("user", prompt)
        reply = ""

        stream = self._client.chat.completions.create(
            model=self._config.llm_primary_model,
            messages=self._messages,
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
        self._log_chat("assistant", reply)
