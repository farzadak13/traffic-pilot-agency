import logging
import streamlit as st
from openai import OpenAI

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def get_openai_client() -> OpenAI | None:
    global _client
    if _client is None:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            return None
        _client = OpenAI(api_key=api_key)
    return _client


def generate_with_openai(
    system_instruction: str,
    user_prompt: str,
    temperature: float = 0.85
) -> str:
    client = get_openai_client()
    if not client:
        logger.warning("OpenAI client not available.")
        return ""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=8192
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return ""