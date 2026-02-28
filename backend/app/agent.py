"""
Gemini-powered agent for drafting messages and processing replies.
Uses LangChain with Google's free Gemini models.
"""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import get_settings


def _get_llm(model_name: str | None = None):
    """Return a Gemini chat model instance."""
    settings = get_settings()
    model = model_name or settings.gemini_model
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.gemini_api_key,
        temperature=0.7,
    )


def draft_message(master_prompt: str, row_data: dict, model_name: str | None = None) -> str:
    """
    Use Gemini to draft a personalized message for one data row.

    Args:
        master_prompt: The user's high-level instruction.
        row_data: The data for this specific row as a dict.
        model_name: Optional model override.

    Returns:
        The drafted message string.
    """
    llm = _get_llm(model_name)

    messages = [
        SystemMessage(content=(
            "You are a professional communication assistant. "
            "Your task is to draft a short, personalized message based on the user's instruction "
            "and the recipient's data. Write ONLY the message body — no subject line, no greeting prefix "
            "like 'Subject:'. Keep it concise, friendly, and professional."
        )),
        HumanMessage(content=(
            f"Instruction: {master_prompt}\n\n"
            f"Recipient data:\n{json.dumps(row_data, indent=2, default=str)}\n\n"
            f"Draft the personalized message now."
        )),
    ]

    response = llm.invoke(messages)
    return response.content.strip()


def process_reply(original_row_data: dict, outbound_message: str, reply_text: str, model_name: str | None = None) -> dict:
    """
    Use Gemini to analyze an inbound reply and extract structured updates.

    Args:
        original_row_data: The original data for this row.
        outbound_message: The message that was sent to the recipient.
        reply_text: The recipient's reply.
        model_name: Optional model override.

    Returns:
        Dict with keys: intent, updates, confidence
    """
    llm = _get_llm(model_name)

    messages = [
        SystemMessage(content=(
            "You are a data extraction assistant. Analyze the reply to a message and extract:\n"
            "1. intent: a short description of what the person is saying (e.g. 'confirmed', 'declined', 'asked question')\n"
            "2. updates: a JSON object with any data fields that should be updated based on the reply\n"
            "3. confidence: a float between 0 and 1 indicating how confident you are in your extraction\n\n"
            "Respond ONLY with valid JSON in this exact format:\n"
            '{"intent": "...", "updates": {...}, "confidence": 0.0}'
        )),
        HumanMessage(content=(
            f"Original data:\n{json.dumps(original_row_data, indent=2, default=str)}\n\n"
            f"Message we sent:\n{outbound_message}\n\n"
            f"Their reply:\n{reply_text}\n\n"
            f"Extract the structured response now."
        )),
    ]

    response = llm.invoke(messages)
    text = response.content.strip()

    # Parse the JSON response — handle markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return valid JSON
        result = {
            "intent": "unclear",
            "updates": {},
            "confidence": 0.3,
        }

    # Ensure all expected keys exist
    result.setdefault("intent", "unclear")
    result.setdefault("updates", {})
    result.setdefault("confidence", 0.5)

    return result
