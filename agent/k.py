"""K — the main agent. Retrieves context, reasons with KLLM, responds."""

from openai import OpenAI
from ..core.config import KLLM_BASE_URL, KLLM_MODEL, KLLM_API_KEY, MAX_TOKENS, STREAM_RESPONSES
from .memory import get_context, get_inventory_context


SYSTEM_PROMPT = """You are K — Kenny's personal AI. You know Kenny well.

Your job:
- Answer questions using what you know about Kenny's profile, preferences, and inventory
- Calibrate depth to Kenny's expertise level in the topic
- Be direct and specific — no generic answers
- When recommending products, always consider what Kenny already owns
- When going deep on a technical topic, match his developer background
- For voice responses, be conversational — no bullet points, no markdown
- Never start from zero — you know this person

{context}
"""


class KAgent:
    def __init__(self, voice_mode: bool = False):
        self.client = OpenAI(base_url=KLLM_BASE_URL, api_key=KLLM_API_KEY)
        self.voice_mode = voice_mode
        self.history = []

    def _build_system(self, query: str) -> str:
        context = get_context(query)

        # Pull inventory context if query seems inventory-related
        inventory_keywords = ["own", "have", "collection", "buy", "worth", "already",
                               "gear", "gun", "jacket", "arcteryx", "patagonia"]
        if any(k in query.lower() for k in inventory_keywords):
            inv = get_inventory_context()
            if inv:
                context = f"{context}\n\n{inv}" if context else inv

        return SYSTEM_PROMPT.format(context=context if context else "No profile data yet — this is an early session.")

    def ask(self, query: str) -> str:
        """Send a query to K and get a response."""
        system = self._build_system(query)

        messages = [{"role": "system", "content": system}]
        messages.extend(self.history[-10:])  # keep last 5 exchanges
        messages.append({"role": "user", "content": query})

        if STREAM_RESPONSES and not self.voice_mode:
            return self._stream(messages)
        else:
            return self._complete(messages)

    def _stream(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=KLLM_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            stream=True,
        )
        full = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full += delta
        print()

        self.history.append({"role": "user", "content": messages[-1]["content"]})
        self.history.append({"role": "assistant", "content": full})
        return full

    def _complete(self, messages: list) -> str:
        response = self.client.chat.completions.create(
            model=KLLM_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = response.choices[0].message.content

        self.history.append({"role": "user", "content": messages[-1]["content"]})
        self.history.append({"role": "assistant", "content": content})
        return content

    def reset_history(self):
        self.history = []
