from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.agent.sub_agents.intent import (
    is_author_request,
    is_identity_request,
    is_rag_request,
    is_researcher_request,
)
from app.agent.sub_agents.author import author_node
from app.agent.sub_agents.common import agent_template, invoke_agent
from app.agent.sub_agents.researcher import ask_researcher, researcher_node
from app.models.claude import haiku_llm
from app.tools.rag.retriever import search as rag_search


orchestrator_chain = (
    agent_template | haiku_llm | StrOutputParser() if haiku_llm else None
)


def orchestrator_node(state):
    request = state["user_input"]
    if is_identity_request(request):
        return {
            "route": "end",
            "rag_context": "",
            "messages": [
                AIMessage(
                    content=(
                        "I am JARVIS, your personal AI assistant. "
                        "I can answer questions, research information, "
                        "and help with writing and other tasks."
                    )
                )
            ],
        }
    lowered_request = request.lower()
    use_rag = (
        is_rag_request(request)
        and "write" not in lowered_request
        and "search" not in lowered_request
    )
    context = ""
    if use_rag:
        context = "\n\n".join(
            filter(
                None,
                (item.get("parent", item.get("text", "")) for item in rag_search(request)),
            )
        )
    if context and use_rag:
        answer = ask_researcher(
            "Answer the user's question using only the supplied vector database context. "
            "If it does not contain the answer, say so clearly.",
            request,
            context,
        )
        return {
            "route": "end",
            "rag_context": context,
            "messages": [AIMessage(content=answer)],
        }
    if use_rag:
        return {
            "route": "end",
            "rag_context": "",
            "messages": [
                AIMessage(
                    content="I could not find that information in your personal references."
                )
            ],
        }
    if is_author_request(request) or is_researcher_request(request):
        return {
            "route": "author" if is_author_request(request) else "researcher",
            "rag_context": context,
        }
    answer = invoke_agent(
        orchestrator_chain,
        "Answer this basic question directly as JARVIS. Do not use web search, "
        "RAG, or authoring unless the user explicitly asks for them.",
        request,
    )
    return {
        "route": "end",
        "rag_context": context,
        "messages": [AIMessage(content=answer)],
    }
