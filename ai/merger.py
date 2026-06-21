import logging
import threading
from ai.gemini_client import generate_with_gemini
from ai.openai_client import generate_with_openai
from ai.prompts import MERGER_SYSTEM_INSTRUCTION
import google.generativeai as genai
import streamlit as st

logger = logging.getLogger(__name__)


def generate_parallel(
    system_instruction: str,
    user_prompt: str
) -> tuple[str, str]:
    results = {"gemini": "", "openai": ""}

    def run_gemini():
        results["gemini"] = generate_with_gemini(
            system_instruction, user_prompt
        )

    def run_openai():
        results["openai"] = generate_with_openai(
            system_instruction, user_prompt
        )

    t1 = threading.Thread(target=run_gemini)
    t2 = threading.Thread(target=run_openai)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    return results["gemini"], results["openai"]


def merge_outputs(
    gemini_output: str,
    openai_output: str,
    brand_name: str
) -> str:
    if not gemini_output and not openai_output:
        return ""
    if not openai_output:
        return gemini_output
    if not gemini_output:
        return openai_output

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        merger_prompt = f"""
دو خروجی برای برند "{brand_name}" تولید شده.
آن‌ها را تحلیل کن و یک نسخه نهایی ترکیبی بهتر بساز.

خروجی اول (Gemini):
{gemini_output}

خروجی دوم (OpenAI):
{openai_output}

اکنون نسخه نهایی را بساز.
"""
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=MERGER_SYSTEM_INSTRUCTION
        )
        response = model.generate_content(
            merger_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192
            )
        )
        return response.text or gemini_output
    except Exception as e:
        logger.error(f"Merger error: {e}")
        return gemini_output


def validate_output(text: str) -> bool:
    """
    بررسی می‌کند که خروجی مدل معتبر است.
    """
    if not text or not text.strip():
        return False
    if len(text.strip()) < 200:
        return False
    return True