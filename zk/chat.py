from config import Configuration
from zk.model import ZK


def run(config: Configuration):
    zk = ZK(config=config)
    while True:
        try:
            line = input(config.PROMPT_CHARACTER + " ")
            if line.strip() in config.EXIT_CHARACTERS:
                break
            if not line.strip():
                continue
            zk.chat(line)
        except (EOFError, KeyboardInterrupt):
            print()
            break
