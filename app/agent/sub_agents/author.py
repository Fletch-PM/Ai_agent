from pathlib import Path
import re

from docx import Document
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser

from app.agent.sub_agents.common import agent_template, invoke_agent
from app.agent.sub_agents.intent import is_document_request
from app.agent.sub_agents.researcher import research_for_author
from app.models.claude import author_llm
from app.prompts.sub_agents.author import author_agent
from app.tools.document.formatter import write_research_document


author_chain = agent_template | author_llm | StrOutputParser() if author_llm else None


def ask_author(prompt, request, context=""):
    return invoke_agent(author_chain, prompt, request, context)


def author_node(state):
    request = state["user_input"]
    context = research_for_author(request, state["rag_context"])
    paper = ask_author(author_agent or "Write the requested paper.", request, context)
    if not is_document_request(request):
        return {"messages": [AIMessage(content=paper)]}
    output_dir = Path("documents")
    output_dir.mkdir(exist_ok=True)
    filename = re.sub(r"[^a-z0-9]+", "_", request.lower()).strip("_")[:50] or "paper"
    path = output_dir / f"{filename}.docx"
    document = Document()
    write_research_document(document, paper)
    document.save(path)
    return {"messages": [AIMessage(content=f"I wrote the paper to `{path}`.")]}
