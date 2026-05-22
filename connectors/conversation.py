from config import Configuration
from zk.model import ZK
from zk.store import Store, Chunk, Source
import uuid


def ingest(
    user_text: str,
    assistant_text: str,
    session_id: str,
    timestamp: str,
    store: Store,
    model: ZK,
    config: Configuration,
):
    pair_text = f"User: {user_text} \n Assistant: {assistant_text}"
    embedding = model.embed(pair_text)
    chunk = Chunk(
        id=uuid.uuid4().hex,
        source=Source.CONVERSATION,
        source_id=session_id,
        timestamp=timestamp,
        embedding=embedding,
        text=pair_text,
        embed_model=config.embed_model,
    )
    store.add([chunk])
