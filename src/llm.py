import os
import sys

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI


def create_llm():
    """
    Create and return a GoogleGenerativeAI model for the workflow.

    Loads environment variables from a local .env file, checks that an
    API key is present, then builds a simple chat model.

    Returns:
        GoogleGenerativeAI: A LangChain chat model ready for chain usage.

    Example:
        llm = create_llm()
        reply = llm.invoke("Say hello in one sentence.")
    """
    # Load values from .env into environment variables.
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key.strip() in {"", "your_api_key_here"}:
        print(
            "ERROR: GOOGLE_API_KEY is missing.\n"
            "Copy .env.example to .env and add your Google Gemini API key."
        )
        sys.exit(1)

    model_name = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

    return GoogleGenerativeAI(api_key=api_key, model=model_name, temperature=0)