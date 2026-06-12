from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    location: str
    source: Literal["google", "tripadvisor"]
    query: str
    results: list
