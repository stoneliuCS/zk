"""
Orchestration layer between ZK and other data sources.
"""

from config import Configuration
from zk.model import ZK
from zk.store import Store
from connectors import conversation
import commands


def run(config: Configuration):
    zk = ZK(config=config)
    store = Store(config=config)
    while True:
        try:
            prompt = input(f"{config.username}: ")
            if not prompt.strip():
                continue
            if prompt.strip().startswith("/"):
                name, _, rest = prompt[1:].partition(" ")
                commands.dispatch(name, rest)
                print("HITT")
                continue

            user_prompt, agent_output, timestamp = zk.chat(prompt, store)
            conversation.ingest(
                user_prompt,
                agent_output,
                zk.get_current_session(),
                timestamp,
                store,
                zk,
                config,
            )
        except (EOFError, KeyboardInterrupt, commands.ExitRepl):
            break
