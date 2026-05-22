from config import Configuration
from zk.chat import run


def main():
    config = Configuration()
    run(config)


if __name__ == "__main__":
    main()
