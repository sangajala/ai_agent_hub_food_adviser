import json
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from agent.state import AgentState
from agent.tools import search_google_maps, search_tripadvisor

TOOLS = [search_google_maps, search_tripadvisor]


def _build_system_prompt(source: str, location: str) -> str:
    source_label = "Google Maps" if source == "google" else "TripAdvisor"
    tool_name = "search_google_maps" if source == "google" else "search_tripadvisor"
    return (
        f"You are a food adviser AI agent. "
        f"The user wants restaurant recommendations in '{location}' using {source_label}. "
        f"You MUST call ONLY the `{tool_name}` tool to fetch results — do not call the other tool. "
        f"After receiving the tool results, present the top options clearly with name, rating, address, and URL."
    )


def agent_node(state: AgentState) -> dict:
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    ).bind_tools(TOOLS)

    system_prompt = _build_system_prompt(state["source"], state["location"])
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return "extract"


def extract_results(state: AgentState) -> dict:
    """Pull raw tool results out of the last ToolMessage and store in state."""
    results = []
    for msg in reversed(state["messages"]):
        if msg.__class__.__name__ == "ToolMessage":
            try:
                results = json.loads(msg.content)
            except (json.JSONDecodeError, TypeError):
                results = []
            break
    return {"results": results}


def build_graph() -> StateGraph:
    tool_node = ToolNode(TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("extract", extract_results)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "extract": "extract"})
    graph.add_edge("tools", "agent")
    graph.add_edge("extract", END)

    return graph.compile()


food_agent = build_graph()
