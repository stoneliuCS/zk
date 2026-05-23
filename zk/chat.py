"""
Orchestration layer between ZK and other data sources.
"""

from typing import Callable
from config import Configuration
from zk.model import ZK
from zk.store import Store
from connectors import conversation
from commands import dispatch
from zk.tui.app import ZKApp


def run(config: Configuration):
    zk = ZK(config=config)
    store = Store(config=config)

    def execute(prompt: str, on_delta: Callable[[str], None]) -> None:
        try:
            if not prompt.strip():
                return
            if prompt.strip().startswith("/"):
                name, _, rest = prompt[1:].partition(" ")
                dispatch(name, rest)
                return
            user_prompt, agent_output, timestamp = zk.chat(prompt, store, on_delta)
            conversation.ingest(
                user_prompt,
                agent_output,
                zk.get_current_session(),
                timestamp,
                store,
                zk,
                config,
            )
        except (EOFError, KeyboardInterrupt):
            return

    app = ZKApp(config, on_submit=execute)
    app.run()
