from typing import TypedDict


class AgentState(TypedDict):
    user_input: str
    messages: list
    route: str
    rag_context: str
