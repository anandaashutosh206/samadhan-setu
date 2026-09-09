import logging

import httpx

from app.config import settings

logger = logging.getLogger("samadhan.ai.llm")


def is_llm_enabled() -> bool:
    return bool(settings.LLM_PROVIDER and settings.LLM_API_KEY)


def get_ai_mode() -> str:
    return "local+llm" if is_llm_enabled() else "local"


async def enrich_summary(text: str, local_summary: str) -> str:
    """Optionally improve the local extractive summary with an LLM call.
    Never raises — any failure silently falls back to the local summary,
    and the API key is never logged."""
    if not is_llm_enabled():
        return local_summary

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            if settings.LLM_PROVIDER.lower() == "anthropic":
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.LLM_API_KEY,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-sonnet-4-6",
                        "max_tokens": 200,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Summarize this civic issue report in 2-3 sentences, plain factual tone:\n\n{text}",
                            }
                        ],
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                blocks = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
                enriched = " ".join(blocks).strip()
                return enriched or local_summary
            else:
                logger.info("Unsupported LLM_PROVIDER '%s'; using local summary.", settings.LLM_PROVIDER)
                return local_summary
    except Exception:
        logger.warning("LLM enrichment failed; falling back to local summary.", exc_info=False)
        return local_summary
