from pydantic import BaseModel, Field

from tools import tool
from zk.store import Store
from zk.model import ZK


class SearchMemoryArgs(BaseModel):
    query: str = Field(
        ...,
        description="What to search for in past conversations and notes.",
    )


@tool(
    input_model=SearchMemoryArgs,
    description=(
        "Search Past conversations and notes for content relevant to a query. "
        "Use this whenever the user asks about something they've discussed before, or "
        "when the current question needs context from past interactions. "
        "Returns up to k matching chunks with their text, source, and timestamp."
    ),
)
def search_memory(args: SearchMemoryArgs, store: Store, model: ZK, **_) -> str:
    embedding = model.embed(args.query)
    results = store.search(embedding)
    if len(results) == 0:
        return "No matching memories found."
    return "\n\n".join(
        f"[{row['timestamp']} · {row['source']}] {row['text']}"
        for row in results.iter_rows(named=True)
    )
