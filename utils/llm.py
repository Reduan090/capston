# utils/llm.py
import ollama
from typing import List, Union, Optional
from config import OLLAMA_MODEL, EMBEDDING_MODEL, logger

# Defer heavy SentenceTransformer import/initialization until embeddings are needed
embedder: Optional[object] = None

def ask_llm(prompt: str, model: str = OLLAMA_MODEL, temperature: float = 0.7) -> str:
    """Unified LLM interface using Ollama.
    
    Args:
        prompt: The input prompt.
        model: Ollama model name.
        temperature: Creativity level (0-1).
    
    Returns:
        Generated text.
    """
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": temperature}
        )
        return response['message']['content']
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise ValueError("Failed to query LLM. Ensure Ollama is running.")

def get_embeddings(texts: Union[str, List[str]]) -> List[List[float]]:
    """Generate embeddings using local model.
    
    Args:
        texts: Single string or list of strings.
    
    Returns:
        List of embedding vectors.
    """
    if isinstance(texts, str):
        texts = [texts]

    # Filter out empty/whitespace-only chunks
    texts = [t for t in texts if t and str(t).strip()]
    if not texts:
        return []

    try:
        # Lazy-init embedder to avoid importing transformers at module import time
        global embedder
        if embedder is None:
            from sentence_transformers import SentenceTransformer
            embedder = SentenceTransformer(EMBEDDING_MODEL)

        embeddings = embedder.encode(texts)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []

    # Handle different return types (numpy array or list)
    try:
        return embeddings.tolist()
    except Exception:
        # If embeddings is already a list of lists
        return list(embeddings)