"""Interview conductor — runs the onboarding session that seeds K's profile."""

import json
from openai import OpenAI
from ..core.config import KLLM_BASE_URL, KLLM_MODEL, KLLM_API_KEY, MAX_TOKENS
from ..core.profile import set_fact, set_domain_expertise, add_preference
from ..core.vector_store import store_fact
from ..core.database import get_conn
from .questions import QUESTIONS, get_all_domains


EXTRACTOR_PROMPT = """You are extracting structured facts from an interview answer.

Given this question and answer, extract the specific facts requested.
Return a JSON object with the extract keys as keys and the extracted values as strings.
If something wasn't mentioned, use null.
Be specific and direct — no filler words.

Question: {question}
Extract keys: {extract_keys}
Answer: {answer}

Return only valid JSON."""


FOLLOW_UP_PROMPT = """You are K, a personal AI assistant conducting an onboarding interview.
You just asked a question and got an answer. Based on the answer, generate ONE natural follow-up
question if the answer was shallow or vague. If the answer was detailed enough, return null.

Question asked: {question}
Answer received: {answer}
Expected depth: {extract_keys}

Return either a follow-up question string, or null. No other text."""


class InterviewConductor:
    def __init__(self):
        self.client = OpenAI(base_url=KLLM_BASE_URL, api_key=KLLM_API_KEY)
        self.completed_ids = set()
        self._load_completed()

    def _load_completed(self):
        """Load already-answered question IDs so we can resume."""
        conn = get_conn()
        rows = conn.execute(
            "SELECT value FROM profile WHERE key LIKE 'interview_q_%'"
        ).fetchall()
        conn.close()
        for row in rows:
            self.completed_ids.add(row["value"])

    def _extract_facts(self, question: dict, answer: str) -> dict:
        """Use LLM to extract structured facts from a free-text answer."""
        try:
            response = self.client.chat.completions.create(
                model=KLLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": EXTRACTOR_PROMPT.format(
                        question=question["question"],
                        extract_keys=question["extract"],
                        answer=answer
                    )
                }],
                max_tokens=256,
                temperature=0.1,
            )
            text = response.choices[0].message.content.strip()
            # Parse JSON, handling markdown code blocks
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"  [extraction failed: {e}]")
            return {}

    def _get_follow_up(self, question: dict, answer: str) -> str | None:
        """Generate a follow-up question if the answer needs more depth."""
        try:
            response = self.client.chat.completions.create(
                model=KLLM_MODEL,
                messages=[{
                    "role": "user",
                    "content": FOLLOW_UP_PROMPT.format(
                        question=question["question"],
                        answer=answer,
                        extract_keys=question["extract"]
                    )
                }],
                max_tokens=100,
                temperature=0.3,
            )
            result = response.choices[0].message.content.strip()
            if result.lower() in ("null", "none", ""):
                return None
            return result
        except Exception:
            return None

    def _store_answer(self, question: dict, answer: str, extracted: dict):
        """Store the answer in profile + vector store."""
        domain = question["domain"]

        # Store raw answer semantically
        store_fact(
            text=f"Q: {question['question']}\nA: {answer}",
            metadata={"type": "interview_answer", "domain": domain,
                      "question_id": question["id"]}
        )

        # Store extracted structured facts
        for key, value in extracted.items():
            if value and value != "null":
                set_fact(key, str(value), domain=domain, source="interview")

        # Mark question as completed
        set_fact(f"interview_q_{question['id']}", question["id"],
                 domain="meta", source="system")
        self.completed_ids.add(question["id"])

    def run(self, resume: bool = True):
        """Run the full interview. Set resume=False to start fresh."""
        if not resume:
            self.completed_ids.clear()

        pending = [q for q in QUESTIONS if q["id"] not in self.completed_ids]

        if not pending:
            print("Interview already complete. Use 'k interview --add' to add more.")
            return

        total = len(QUESTIONS)
        done = total - len(pending)

        print(f"\n{'='*60}")
        print("  K — Onboarding Interview")
        print(f"  {done}/{total} questions answered")
        print(f"{'='*60}")
        print("\nI'm going to ask you questions across several areas to build")
        print("your profile. Be as specific as you want — more detail means")
        print("better recommendations. Type 'skip' to skip any question.\n")

        for i, question in enumerate(pending, done + 1):
            print(f"\n[{i}/{total}] {question['question']}")
            answer = input("  → ").strip()

            if answer.lower() == "skip":
                print("  Skipped.")
                continue

            if not answer:
                continue

            # Extract structured facts
            print("  [processing...]", end="\r")
            extracted = self._extract_facts(question, answer)

            # Offer follow-up if answer was shallow
            follow_up = self._get_follow_up(question, answer)
            if follow_up:
                print(f"\n  {follow_up}")
                follow_up_answer = input("  → ").strip()
                if follow_up_answer and follow_up_answer.lower() != "skip":
                    answer = f"{answer}. {follow_up_answer}"
                    extracted.update(self._extract_facts(question, follow_up_answer))

            self._store_answer(question, answer, extracted)
            print(f"  ✓ Noted")

        print(f"\n{'='*60}")
        print("  Interview complete. K now knows you.")
        print(f"{'='*60}\n")
