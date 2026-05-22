import lancedb
from lancedb.pydantic import LanceModel, Vector
from config import Configuration
from enum import StrEnum
import polars as pl

CHUNK_EMBEDDING_SIZE = 768


class Source(StrEnum):
    CONVERSATION = "conversation"


class Chunk(LanceModel):
    id: str
    source_id: str
    text: str
    embedding: Vector(CHUNK_EMBEDDING_SIZE)  # type: ignore[reportInvalidTypeForm]
    source: str # Enumeration Type.
    timestamp: str
    embed_model: str


class Store:
    def __init__(self, config: Configuration) -> None:
        self._config = config
        self._db = lancedb.connect(self._config.db_uri)
        self._table = self._db.create_table("chunks", schema=Chunk, exist_ok=True)
        self._k = 5

    def add(self, chunks: list[Chunk]):
        self._table.add([c.model_dump() for c in chunks])

    def search(self, query: list[float]) -> pl.DataFrame:
        """
        Takes in a query vector and searches the current store for relevant information
        """
        q = self._table.search(query).limit(self._k)
        return q.to_polars()
