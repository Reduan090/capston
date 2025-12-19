# utils/api_helpers.py
from semanticscholar import SemanticScholar
import arxiv
try:
    from habanero import Crossref, counts
    HAS_HABANERO = True
except ImportError:
    Crossref = None
    counts = None
    HAS_HABANERO = False

from typing import List, Dict, Any
import time
from config import SEMANTIC_SCHOLAR_API_KEY, logger

cr = Crossref() if HAS_HABANERO else None
sch = SemanticScholar(api_key=SEMANTIC_SCHOLAR_API_KEY) if SEMANTIC_SCHOLAR_API_KEY else SemanticScholar()

def fetch_papers(query: str, limit: int = 10) -> List[Dict]:
    """Fetch papers from Semantic Scholar with rate limit handling."""
    try:
        results = sch.search_paper(query, limit=limit)
        return [paper.raw_data for paper in results]  # Raw for details
    except Exception as e:
        logger.error(f"Semantic Scholar error: {e}")
        time.sleep(1)  # Rate limit backoff
        return []

def fetch_by_doi(doi: str) -> Dict[str, Any]:
    """Fetch by DOI using CrossRef."""
    if not HAS_HABANERO or cr is None:
        logger.warning("habanero not available - install with: pip install habanero")
        return {}
    try:
        return cr.works(ids=doi)['message']
    except Exception as e:
        logger.error(f"CrossRef error: {e}")
        return {}

def fetch_arxiv(query: str, limit: int = 10) -> List[Dict]:
    """Fetch from arXiv."""
    search = arxiv.Search(query=query, max_results=limit)
    return [vars(result) for result in search.results()]

def fetch_unpaywall(doi: str) -> Dict:
    """Fetch open access URL (requires email)."""
    import requests
    url = f"https://api.unpaywall.org/{doi}?email=your@email.com"  # Replace email
    try:
        response = requests.get(url)
        return response.json() if response.ok else {}
    except Exception as e:
        logger.error(f"Unpaywall error: {e}")
        return {}