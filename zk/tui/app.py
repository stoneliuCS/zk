from typing import Callable

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Input, Static
from textual import work

from commands import ExitRepl
from config import Configuration

type OnSubmit = Callable[[str, Callable[[str], None]], None]


class ZKApp(App):
    CSS = """
    Screen { background: black; color: white; }
    #messages { padding: 1 2; background: black; }
    .msg { margin-bottom: 1; }
    .user { color: cyan; }
    .error { color: red; }
    Input {
        dock: bottom;
        background: black;
        color: white;
        border: round white;
        padding: 0 1;
        height: 3;
        margin: 0 2 1 2;
    }
    Input:focus { background: black; background-tint: black 0%; }
    Input.-blurred { background: black; background-tint: black 0%; }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "Quit")]

    def __init__(self, config: Configuration, on_submit: OnSubmit) -> None:
        super().__init__()
        self.username = config.username
        self.agent_name = "ZK"
        self._on_submit = on_submit
        self._live: Static | None = None
        self._live_buffer = ""

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="messages")
        yield Input(placeholder="…", id="input")

    def on_mount(self) -> None:
        self.query_one("#input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        self.query_one("#input", Input).value = ""
        if not text:
            return
        self._add_message(f"{self.username}: {text}", "user")
        self._dispatch(text)

    def _add_message(self, text: str, css_class: str = "") -> None:
        msg = Static(text, classes=f"msg {css_class}".strip(), markup=False)
        scroll = self.query_one("#messages", VerticalScroll)
        scroll.mount(msg)
        scroll.scroll_end(animate=False)

    def _append_delta(self, chunk: str) -> None:
        scroll = self.query_one("#messages", VerticalScroll)
        live = self._live
        if live is None:
            self._live_buffer = f"{self.agent_name}: "
            live = Static(self._live_buffer, classes="msg", markup=False)
            self._live = live
            scroll.mount(live)
        self._live_buffer += chunk
        live.update(self._live_buffer)
        scroll.scroll_end(animate=False)

    def _commit_assistant(self) -> None:
        self._live = None
        self._live_buffer = ""

    @work(thread=True)
    def _dispatch(self, text: str) -> None:
        def on_delta(chunk: str) -> None:
            self.call_from_thread(self._append_delta, chunk)

        try:
            self._on_submit(text, on_delta)
            self.call_from_thread(self._commit_assistant)
        except ExitRepl:
            self.call_from_thread(self.exit)
        except Exception as e:
            self.call_from_thread(
                self._add_message, f"error: {type(e).__name__}: {e}", "error"
            )
