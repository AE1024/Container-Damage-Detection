import re
import json
import base64
import os
import pathlib
from typing import Any

from groq import Groq, BadRequestError
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

_USER_MESSAGES = lambda b64: [
    {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
            {"type": "text", "text": "What is the ISO container code in this image? It has exactly 4 uppercase letters followed by 7 digits (e.g. MSCU1234567). Call submit_container_code with the result."},
        ],
    }
]


def _call_without_tools(b64: str) -> str:
    """Tool calling başarısız olduğunda sade metin isteği atar, regex ile kodu çeker."""
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an OCR tool. Reply with ONLY the ISO container code "
                    "(4 uppercase letters + 7 digits, e.g. MSCU1234567). "
                    "No explanation, no punctuation, just the code. "
                    "If not visible, reply with NONE."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {"type": "text", "text": "Container code?"},
                ],
            },
        ],
        max_tokens=20,
        temperature=0.0,
        reasoning_effort="none",
    )
    text = (resp.choices[0].message.content or "").upper()
    match = _CODE_RE.search(text)
    return match.group(0) if match else ""


def extract_bic_code(image_bytes: bytes) -> str:
    """Görüntü byte'larından ISO konteyner kodunu Groq ile çıkarır.
    Önce tool calling dener; başarısız olursa sade metin isteğine geçer.
    """
    b64 = base64.b64encode(image_bytes).decode()
    try:
        resp = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a container code extractor. "
                        "You MUST call submit_container_code with the ISO code (4 letters + 7 digits). "
                        "Do NOT write any text. Only call the function."
                    ),
                },
                *_USER_MESSAGES(b64),
            ],
            tools=[_TOOL],
            tool_choice="required",
            max_tokens=32,
            temperature=0.0,
            reasoning_effort="none",
        )
        tool_calls = resp.choices[0].message.tool_calls
        raw = json.loads(tool_calls[0].function.arguments).get("container_code", "") if tool_calls else ""
        match = _CODE_RE.search(raw.upper())
        return match.group(0) if match else ""

    except BadRequestError as e:
        # Model düz metin döndürdüğünde Groq 400 atar
        body = getattr(e, "body", {}) or {}
        failed_gen = body.get("error", {}).get("failed_generation", "")
        match = _CODE_RE.search(failed_gen.upper()) if failed_gen else None
        if match:
            print(f"[LLM] failed_generation'dan alındı: {match.group(0)}")
            return match.group(0)
        # failed_generation kesik kaldıysa tool'suz ikinci deneme
        print("[LLM] failed_generation yetersiz, tool'suz deneme yapılıyor…")
        try:
            return _call_without_tools(b64)
        except Exception as e2:
            print(f"[LLM] Tool'suz deneme de başarısız: {e2}")
            return ""

    except Exception as e:
        print(f"[LLM] Hata: {e}")
        return ""
