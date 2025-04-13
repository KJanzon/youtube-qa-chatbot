from difflib import SequenceMatcher
from typing import List, Dict


def rank_sources_by_chapter_similarity(query: str, sources: List, chapters: List[Dict]) -> List:
    """
    Prioritize transcript chunks whose chapter title best matches the query.
    """
    def similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    if not chapters:
        return sources

    best_match = max(chapters, key=lambda c: similarity(query, c["title"]), default=None)

    if best_match and similarity(query, best_match["title"]) > 0.5:
        preferred = [doc for doc in sources
                     if doc.metadata.get("chapter_title", "").lower() == best_match["title"].lower()]
        rest = [doc for doc in sources if doc not in preferred]
        return preferred + rest

    return sources