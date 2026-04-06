"""Research orchestration — multi-step search, read, synthesize personalized to Kenny."""

import json
from openai import OpenAI
from .search import search, SearchResult
from .reader import read_url
from ..memory import get_context, get_inventory_context
from ...core.config import KLLM_BASE_URL, KLLM_MODEL, KLLM_API_KEY
from ...core.database import get_conn


# ── Prompts ───────────────────────────────────────────────────────────────────

QUERY_PLANNER_PROMPT = """You are helping Kenny research something. Based on his query and profile,
generate 2-3 specific web search queries that will find the most relevant information.

Kenny's profile context:
{profile_context}

Kenny's query: {query}

Return a JSON array of search query strings. Be specific — include product names, years,
"review", "vs", or other qualifiers that get better results. No other text.

Example: ["Arcteryx Atom LT SL AR comparison 2024 2025", "Arcteryx Atom new release review worth buying"]"""


RESULT_SCORER_PROMPT = """Given these search results and Kenny's query, pick the 3 most useful
URLs to read in full. Consider: relevance, source quality (prefer reviews, official sites,
enthusiast forums over ads/spam).

Query: {query}
Results:
{results_text}

Return a JSON array of URLs (max 3). No other text."""


SYNTHESIZER_PROMPT = """You are K — Kenny's personal AI. You've researched his question using
live web data. Now synthesize a personalized answer.

Kenny's profile (relevant to this query):
{profile_context}

{inventory_context}

Kenny's question: {query}

Research findings:
{research_text}

Instructions:
- Answer directly and specifically to Kenny's situation
- Reference what he already owns when relevant (don't recommend what he has)
- Call out the specific delta — what's new, what's better, what's the gap
- Give a clear recommendation if asked for one
- Cite sources inline naturally (e.g. "according to [site]...")
- Match his expertise level — he goes deep, don't oversimplify
- If research was inconclusive, say so and explain what's missing"""


class Researcher:
    def __init__(self):
        self.client = OpenAI(base_url=KLLM_BASE_URL, api_key=KLLM_API_KEY)

    def _llm(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> str:
        response = self.client.chat.completions.create(
            model=KLLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    def _parse_json(self, text: str) -> list:
        """Parse JSON array from LLM output, handling markdown fences."""
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        try:
            result = json.loads(text)
            return result if isinstance(result, list) else []
        except Exception:
            return []

    def plan_queries(self, query: str, profile_context: str) -> list[str]:
        """Generate targeted search queries for this question."""
        print("  Planning searches...", flush=True)
        result = self._llm(QUERY_PLANNER_PROMPT.format(
            profile_context=profile_context[:1000],
            query=query
        ))
        queries = self._parse_json(result)
        return queries[:3] if queries else [query]

    def gather_results(self, queries: list[str]) -> list[SearchResult]:
        """Run all searches and deduplicate."""
        seen_urls = set()
        all_results = []

        for q in queries:
            print(f"  Searching: {q}", flush=True)
            results = search(q, max_results=6)
            for r in results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    all_results.append(r)

        return all_results

    def select_urls(self, query: str, results: list[SearchResult]) -> list[str]:
        """Use LLM to pick the most useful URLs to read."""
        if not results:
            return []

        results_text = "\n".join(
            f"{i+1}. [{r.title}] {r.url}\n   {r.snippet[:150]}"
            for i, r in enumerate(results)
        )

        result = self._llm(RESULT_SCORER_PROMPT.format(
            query=query,
            results_text=results_text
        ), max_tokens=200)

        return self._parse_json(result)[:3]

    def read_pages(self, urls: list[str]) -> list[dict]:
        """Fetch and extract content from selected URLs."""
        pages = []
        for url in urls:
            print(f"  Reading: {url[:60]}...", flush=True)
            page = read_url(url)
            if page:
                pages.append({
                    "url": page.url,
                    "title": page.title,
                    "text": page.text[:3000]  # cap per page
                })
        return pages

    def synthesize(self, query: str, pages: list[dict],
                   profile_context: str, inventory_context: str) -> str:
        """Synthesize research into a personalized answer, streamed."""
        if not pages:
            research_text = "No useful pages could be retrieved. Answer based on general knowledge."
        else:
            parts = []
            for p in pages:
                parts.append(f"SOURCE: {p['title']} ({p['url']})\n{p['text']}")
            research_text = "\n\n---\n\n".join(parts)

        prompt = SYNTHESIZER_PROMPT.format(
            profile_context=profile_context,
            inventory_context=inventory_context,
            query=query,
            research_text=research_text[:6000]  # stay within context
        )

        # Stream the synthesis
        response = self.client.chat.completions.create(
            model=KLLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.4,
            stream=True,
        )

        full = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full += delta
        print()

        # Save to research history
        self._save_research(query, full)
        return full

    def _save_research(self, query: str, result: str):
        conn = get_conn()
        conn.execute(
            "INSERT INTO research (query, result) VALUES (?, ?)",
            (query, result[:2000])
        )
        conn.commit()
        conn.close()

    def run(self, query: str) -> str:
        """Full research pipeline — plan → search → read → synthesize."""
        print("\n[K Research]")

        profile_context = get_context(query)
        inventory_context = get_inventory_context()

        # Plan targeted search queries
        queries = self.plan_queries(query, profile_context)

        # Gather search results
        results = self.gather_results(queries)
        if not results:
            return "Couldn't retrieve search results. Check your connection."

        # Select best URLs to read
        urls = self.select_urls(query, results)

        # Read full pages
        pages = self.read_pages(urls) if urls else []

        # Synthesize personalized answer
        print("\nK: ", end="", flush=True)
        return self.synthesize(query, pages, profile_context, inventory_context)
