import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

sonnet_llm = (
    ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-5-5",
        temperature=0,
        api_key=api_key,
    )
    if api_key
    else None
)

haiku_llm = (
    ChatAnthropic(
        model=os.getenv("ANTHROPIC_HAIKU_MODEL") or "claude-haiku-4-5",
        temperature=0,
        api_key=api_key,
    )
    if api_key
    else None
)

author_llm = (
    ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-5-5",
        temperature=0,
        max_tokens=int(os.getenv("ANTHROPIC_AUTHOR_MAX_TOKENS", "5000")),
        api_key=api_key,
    )
    if api_key
    else None
)

gen_llm = sonnet_llm