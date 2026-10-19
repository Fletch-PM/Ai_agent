from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.prompts.agent_identity import agent_identity_sp


agent_template = ChatPromptTemplate.from_messages(
    [
        ("system", agent_identity_sp),
        (
            "human",
            "Tool status:\n{tool_instruction}\n\nContext:\n{context}\n\nQuestion:\n{user_input}",
        ),
    ]
)


def invoke_agent(chain, prompt, request, context=""):
    if chain is None:
        return context or "Please set ANTHROPIC_API_KEY before starting the agent."
    return chain.invoke(
        {"user_input": request, "context": context, "tool_instruction": prompt}
    )
