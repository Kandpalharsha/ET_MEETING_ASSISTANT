import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _make_llm(temperature: float = 0.1) -> ChatGroq:
    return ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=temperature,
        max_retries=3,
        request_timeout=30,
    )


# Main reasoning LLM
llm = _make_llm(temperature=0.1)

# Deterministic LLM for structured extraction
llm_strict = _make_llm(temperature=0.0)

# JSON output chain — extraction agent uses this
llm_json = llm_strict | JsonOutputParser()
