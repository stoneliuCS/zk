from commands import ExitRepl, command


@command(description="Exits the CLI session.")
def exit(_: str, **__):
    raise ExitRepl()


@command(description="Exits the CLI session.")
def quit(_: str, **__):
    raise ExitRepl()
