"""
Responsible for interfacing with the actual module client.
"""

from typing import Literal
from openai import OpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam

from config import Configuration
from zk.transcripts import append
from zk.store import Store
from datetime import datetime, UTC
import tools


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
        self._name = "ZK"
        self._max_iterations = 5

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

    def _output_chunk(self, chunk: ChatCompletionChunk, replies) -> None:
        delta = chunk.choices[0].delta.content
        if not delta:
            return
        print(delta, end="", flush=True)
        replies.append(delta)

    def _stream_and_collect(self, to_send: list[ChatCompletionMessageParam]):
        tool_buffer: dict[int, dict] = {}
        finish_reason = None
        replies = []

        stream = self._client.chat.completions.create(
            model=self._config.llm_primary_model,
            messages=to_send,
            tools=tools.get_schemas(),
            tool_choice="auto",
            stream=True,
        )

        print(f"{self._name}: ", end="", flush=True)
        for chunk in stream:
            choice = chunk.choices[0]
            delta = choice.delta
            self._output_chunk(chunk, replies)

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    slot = tool_buffer.setdefault(
                        tc.index, {"id": "", "name": "", "arguments": ""}
                    )
                    if tc.id:
                        slot["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            slot["name"] += tc.function.name
                        if tc.function.arguments:
                            slot["arguments"] += tc.function.arguments
            if choice.finish_reason:
                finish_reason = choice.finish_reason

        tool_calls = [
            {
                "id": tool_buffer[i]["id"],
                "type": "function",
                "function": {
                    "name": tool_buffer[i]["name"],
                    "arguments": tool_buffer[i]["arguments"],
                },
            }
            for i in sorted(tool_buffer.keys())
        ]

        content = "".join(replies)
        if content:
            print()

        return {
            "content": content,
            "tool_calls": tool_calls,
            "finish_reason": finish_reason,
        }

    def _execute_chat(
        self,
        to_send: list[ChatCompletionMessageParam],
        prompt: str,
        store: Store,
        timestamp: str,
    ) -> tuple[str, str, str]:
        for _ in range(self._max_iterations):
            result = self._stream_and_collect(to_send)

            if not result["tool_calls"]:
                reply = result["content"]
                self._messages.append({"role": "assistant", "content": reply})
                self._log_chat("assistant", reply, timestamp)
                return (prompt, reply, timestamp)

            assistant_msg: ChatCompletionMessageParam = {
                "role": "assistant",
                "content": result["content"] or None,
                "tool_calls": result["tool_calls"],
            }

            to_send.append(assistant_msg)
            self._messages.append(assistant_msg)

            for call in result["tool_calls"]:
                print(f"\n[calling {call['function']['name']}...]")
                tool_result = tools.dispatch(
                    call["function"]["name"],
                    call["function"]["arguments"],
                    store=store,
                    model=self,
                )
                tool_msg: ChatCompletionMessageParam = {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": tool_result,
                }
                to_send.append(tool_msg)
                self._messages.append(tool_msg)

        fallback = "I'm having trouble finishing that. Could you rephrase?"
        self._messages.append({"role": "assistant", "content": fallback})
        self._log_chat("assistant", fallback, timestamp)
        return (prompt, fallback, timestamp)

    def chat(self, prompt: str, store: Store) -> tuple[str, str, str]:
        """
        Chats with the ZK Model. Returns the prompt of the user, the response by ZK, and the timestamp.
        """
        self._messages.append({"role": "user", "content": prompt})
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self._log_chat("user", prompt, timestamp)

        to_send = list(self._messages)

        return self._execute_chat(to_send, prompt, store, timestamp)

    def embed(self, text: str):
        res = self._client.embeddings.create(input=text, model=self._config.embed_model)
        return res.data[0].embedding

    def get_current_session(self) -> str:
        return self._session
