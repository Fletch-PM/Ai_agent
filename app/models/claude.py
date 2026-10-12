import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

sonnet_llm = (
    ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-4-6",
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

gen_llm = sonnet_llm