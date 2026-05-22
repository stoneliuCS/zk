from config import Configuration
from zk.model import ZK
from zk.store import Store
import polars as pl
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def _retrieval_debug_logging(chunks: pl.DataFrame) -> None:
    logger.debug("retrieved %d chunks", len(chunks))
    for row in chunks.iter_rows(named=True):
        logger.debug(
            "  d=%.3f source=%s ts=%s text=%r",
            row["_distance"],
            row["source"],
            row["timestamp"],
            row["text"][:80],
        )


def _format_as_context(chunks: pl.DataFrame, config: Configuration) -> str:
    now = datetime.now().astimezone().strftime("%A, %Y-%m-%d %H:%M %Z")
    parts = [f"<current_time>{now}</current_time>"]
    if config.location:
        parts.append(f"<user_location{config.location}</user_location>")

    if len(chunks) > 0:
        lines = [
            f"[{row['timestamp']} · {row['source']}] {row['text']}"
            for row in chunks.iter_rows(named=True)
        ]
        parts.append("<past_context>\n" + "\n\n".join(lines) + "\n</past_context>")

    return "\n".join(parts)


def retrieve(query: str, store: Store, model: ZK, config: Configuration) -> str:
    query_vector = model.embed(query)
    chunks = store.search(query_vector)
    _retrieval_debug_logging(chunks)
    return _format_as_context(chunks, config)
