from config import Configuration
from zk.chat import run
from zk.log import setup
import pkgutil, importlib, tools, commands


def _boot_strap():
    for m in pkgutil.iter_modules(tools.__path__):
        importlib.import_module(f"tools.{m.name}")
    for m in pkgutil.iter_modules(commands.__path__):
        importlib.import_module(f"commands.{m.name}")


def main():
    _boot_strap()
    config = Configuration()
    if config.debug:
        setup()
    run(config)


if __name__ == "__main__":
    main()
