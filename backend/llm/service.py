import re
import json
import base64
import os
import pathlib
from typing import Any

from groq import Groq
from dotenv import load_dotenv

load_dotenv(pathlib.Path(__file__).resolve().parent.parent.parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

_MODEL = "qwen/qwen3.6-27b"
_CODE_RE = re.compile(r"[A-Z]{4}\d{7}")

_TOOL: Any = {
    "type": "function",
    "function": {
        "name": "submit_container_code",
        "description": "Submit the ISO container code found in the image.",
        "parameters": {
            "type": "object",
            "properties": {
                "container_code": {
                    "type": "string",
                    "description": "4 uppercase letters + 7 digits (e.g. MSCU1234567). Empty string if not visible.",
                }
            },
            "required": ["container_code"],
        },
    },
}


def extract_bic_code(image_bytes: bytes) -> str:
    """Görüntü byte'larından ISO konteyner kodunu Groq tool calling ile çıkarır."""
    b64 = base64.b64encode(image_bytes).decode()
    try:
        resp = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You extract ISO container codes from images. Always call submit_container_code.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is the container code (4 letters + 7 digits) in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    ],
                },
            ],
            tools=[_TOOL],
            tool_choice="required",
            max_tokens=64,
            temperature=0.0,
            reasoning_effort="none",
        )
        tool_calls = resp.choices[0].message.tool_calls
        raw = json.loads(tool_calls[0].function.arguments).get("container_code", "") if tool_calls else ""
        match = _CODE_RE.search(raw.upper())
        return match.group(0) if match else ""
    except Exception as e:
        print(f"[LLM] Hata: {e}")
        return ""
