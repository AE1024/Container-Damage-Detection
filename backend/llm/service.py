import re
import json
import base64
import pathlib
import os
from typing import cast

from groq import Groq
from groq.types.chat import ChatCompletionToolParam
from dotenv import load_dotenv

_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

TOOL: ChatCompletionToolParam = cast(ChatCompletionToolParam, {
    "type": "function",
    "function": {
        "name": "submit_container_code",
        "description": "Submit the ISO container code found in the image",
        "parameters": {
            "type": "object",
            "properties": {
                "container_code": {
                    "type": "string",
                    "description": "4 uppercase letters + 7 digits (e.g. MSCU1234567). Empty string if not found.",
                }
            },
            "required": ["container_code"],
        },
    },
})


def extract_bic_code(image_bytes: bytes) -> str:
    """Kırpılmış konteyner görseli alır, Qwen vision + tool calling ile ISO kodunu döner."""
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Read the shipping container ISO code from this image. "
                                "It is 4 uppercase letters followed by 7 digits (e.g. MSCU1234567). "
                                "Call submit_container_code with the code."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"},
                        },
                    ],
                }
            ],
            tools=[TOOL],
            tool_choice="auto",
            max_tokens=64,
            temperature=0.0,
            reasoning_effort="none",
        )

        msg = response.choices[0].message
        tool_calls = msg.tool_calls

        if not tool_calls:
            raw = re.sub(r"<think>.*?</think>", "", msg.content or "", flags=re.DOTALL).strip()
            print(f"[LLM] Tool call yok, içerik: '{raw}'")
            match = re.search(r"[A-Z]{4}\d{7}", raw)
            return match.group(0) if match else ""

        raw = json.loads(tool_calls[0].function.arguments).get("container_code", "")
        print(f"[LLM] Qwen sonucu: '{raw}'")
        match = re.search(r"[A-Z]{4}\d{7}", raw.upper())
        return match.group(0) if match else ""

    except Exception as e:
        print(f"[LLM] Hata: {e}")
        return ""
