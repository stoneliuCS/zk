from config import Configuration
from zk.chat import run
from zk.log import setup
import tools.search_memory


def main():
    config = Configuration()
    if config.debug:
        setup()
    run(config)


if __name__ == "__main__":
    main()
