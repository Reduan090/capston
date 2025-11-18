# utils/llm.py
import ollama
from sentence_transformers import SentenceTransformer
from typing import List, Union
from config import OLLAMA_MODEL, EMBEDDING_MODEL, logger

embedder = SentenceTransformer(EMBEDDING_MODEL)

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
    return embedder.encode(texts).tolist()