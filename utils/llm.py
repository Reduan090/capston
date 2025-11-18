# utils/llm.py
import os
from typing import List, Union
from sentence_transformers import SentenceTransformer
from config import OLLAMA_MODEL, EMBEDDING_MODEL, logger


# Try to import ollama; if it's not available, fall back to a safe mock mode.
_OLLAMA_AVAILABLE = True
try:
    import ollama  # type: ignore
except Exception:
    _OLLAMA_AVAILABLE = False
    logger.warning("Ollama client not available; falling back to mock LLM responses.")

# Initialize embedder (will download model if needed)
embedder = SentenceTransformer(EMBEDDING_MODEL)


def ask_llm(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.7) -> str:
    """Unified LLM interface.

    Behavior:
    - If Ollama client is available and reachable, call the local LLM.
    - Otherwise, return a lightweight deterministic mock response so the
      application and tests can run without a local Ollama server installed.

    The mock mode can be overridden by installing Ollama and running
    `ollama serve` locally.
    """
    # If Ollama client is present, attempt a real call. If it fails, log and
    # fall back to the mock response to avoid crashing the app during dev.
    if _OLLAMA_AVAILABLE:
        try:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": temperature}
            )
            # Ollama client returns a dict-like response
            return response.get('message', {}).get('content', '')
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")

    # Mock fallback (deterministic and safe): return a short echo-like reply.
    logger.info("Using mock LLM response (install/run Ollama to get real responses).")
    return f"[MOCK LLM] {prompt[:200]}"


def get_embeddings(texts: Union[str, List[str]]) -> List[List[float]]:
    """Generate embeddings using the configured SentenceTransformer model.

    Returns a list of float vectors. If a single string is provided, a single
    vector (inside a list) is returned.
    """
    if isinstance(texts, str):
        texts = [texts]
    return embedder.encode(texts).tolist()