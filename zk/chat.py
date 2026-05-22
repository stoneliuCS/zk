"""
Orchestration layer between ZK and other data sources.
"""

from config import Configuration
from zk.model import ZK
from zk.store import Store
from zk.retrieval import retrieve
from connectors import conversation
import logging

logger = logging.getLogger(__name__)


def run(config: Configuration):
    zk = ZK(config=config)
    store = Store(config=config)
    while True:
        try:
            prompt = input(config.PROMPT_CHARACTER + " ")
            if prompt.strip() in config.EXIT_CHARACTERS:
                break
            if not prompt.strip():
                continue
            context = retrieve(prompt, store, zk, config)
            logger.debug("Context: ", context)
            user_prompt, agent_output, timestamp = zk.chat(prompt, context)
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
