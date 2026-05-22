import logging


def setup() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s %(levelname)s %(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
