"""
Orchestration layer between ZK and other data sources.
"""

from config import Configuration
from zk.model import ZK
from zk.store import Store
from connectors import conversation


def run(config: Configuration):
    zk = ZK(config=config)
    store = Store(config=config)
    while True:
        try:
            prompt = input(f"{config.username}: ")
            if prompt.strip() in config.EXIT_CHARACTERS:
                break
            if not prompt.strip():
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
        except (EOFError, KeyboardInterrupt):
            print()
            break
