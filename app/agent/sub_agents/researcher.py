from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.agent.sub_agents.common import agent_template, invoke_agent
from app.models.claude import haiku_llm
from app.prompts.sub_agents.researcher import researcher_agent
from app.tools.weather.weather_search import is_weather_query, weather_search
from app.tools.websearch.search_intents import extract_search_query, match_search_intent
from app.tools.websearch.web_search import web_search


researcher_chain = (
    agent_template | haiku_llm | StrOutputParser() if haiku_llm else None
)


def ask_researcher(prompt, request, context=""):
    return invoke_agent(researcher_chain, prompt, request, context)


def research(request, reference_context=""):
    query = extract_search_query(request) if match_search_intent(request) else request
    if is_weather_query(query):
        results = weather_search(query)
    else:
        results = web_search(query)
    search_context = "\n\n".join(
        f"Title: {item.get('title', 'Reference')}\n"
        f"Summary: {item.get('snippet', item.get('parent', item.get('text', '')))}\n"
        f"URL: {item.get('url', 'local reference')}"
        for item in results
    )
    context = "\n\n".join(filter(None, (reference_context, search_context)))
    return ask_researcher(
        researcher_agent or "Use the research results to answer the request.",
        request,
        context,
    )


def research_for_author(request, reference_context=""):
    """Research an author request using its topic as a direct search query."""
    query = re.sub(
        r"^\s*(?:please\s+)?(?:write|draft|create|compose|generate|make)\b",
        "",
        request,
        flags=re.IGNORECASE,
    )
    query = re.sub(
        r"\b(?:a|an)?\s*(?:research\s+paper|paper|essay|article|report|"
        r"docx?\s+file|docs?\s+file|word\s+(?:document|file))\b",
        "",
        query,
        flags=re.IGNORECASE,
    )
    query = re.sub(
        r"^\s*(?:about|on|regarding|concerning|for)\s+",
        "",
        query,
        flags=re.IGNORECASE,
    ).strip(" .?!,:;")
    return research(
        f"Search the web for {query}",
        reference_context,
    )


def researcher_node(state):
    return {"messages": [AIMessage(content=research(state["user_input"], state["rag_context"]))]}
import re
