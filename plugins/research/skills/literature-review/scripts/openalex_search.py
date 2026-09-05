#!/usr/bin/env python3
"""OpenAlex search client for the literature-review skill.

Queries the public OpenAlex API (https://api.openalex.org/works) and returns structured paper metadata as JSON. No API key required.

OpenAlex provides several advantages for literature reviews:

- Citation counts for ranking papers by impact
- Date-range filtering with sort-by-citation-count
- Reverse citation graph via the ``cites:`` filter (find papers that cite a given work)
- Topic clustering via ``group_by=primary_topic.id``
- Rich metadata: DOIs, concepts, open-access PDF links, related works

Design notes:

- No additional dependencies required. Uses ``requests`` when available, falls back to ``urllib`` with a requests-compatible shim.
- The ``mailto`` parameter is appended to every request for the OpenAlex politeness pool — it gives us faster, more reliable responses. The default email can be overridden via ``--email`` or the ``OPENALEX_EMAIL`` environment variable.
- OpenAlex abstracts are stored as an *inverted index* (word → list of positions). We reconstruct the original text by reversing the index. Some works have no abstract (``null``); those get an empty string.
- The arXiv ID is extracted from the work's ``locations`` array — we look for a location whose source is the arXiv repository.
- ``max_results`` is clamped to 50 to match the skill's documented upper bound.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

OPENALEX_ENDPOINT = "https://api.openalex.org/works"
MAX_RESULTS_UPPER_BOUND = 50
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_EMAIL = "havtorn93@gmail.com"


# --- HTTP client with requests -> urllib fallback --------------------------

try:
    import requests  # type: ignore
except ImportError:
    import urllib.error
    import urllib.parse
    import urllib.request

    class _UrllibResponse:
        def __init__(self, data: bytes, status: int) -> None:
            self._data = data
            self.status_code = status
            self.text = data.decode("utf-8", errors="replace")
            self.content = data

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise RuntimeError(f"HTTP {self.status_code}")

    class _UrllibRequestsShim:
        """Minimal requests-compatible shim using urllib.

        Only supports what openalex_search needs: GET with query params. Params are encoded with quote_plus so multi-word queries work.
        """

        @staticmethod
        def get(url: str, params: dict | None = None, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> _UrllibResponse:
            if params:
                query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
                url = f"{url}?{query}"
            req = urllib.request.Request(
                url, headers={"User-Agent": "literature-review-skill/0.3 (mailto:openalex)"}
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return _UrllibResponse(resp.read(), resp.status)
            except urllib.error.HTTPError as e:
                return _UrllibResponse(e.read(), e.code)

    requests = _UrllibRequestsShim()  # type: ignore


# --- Core query + parsing --------------------------------------------------


def _reconstruct_abstract(inverted_index: dict | None) -> str:
    """Rebuild abstract text from OpenAlex's inverted index.

    OpenAlex stores abstracts as ``{word: [pos1, pos2, ...]}``. We reverse this into a flat list of (position, word) pairs,
    sort by position, and join with spaces. Returns an empty string when the inverted index is null or empty.
    """
    if not inverted_index:
        return ""
    indexed = sorted((pos, word) for word, positions in inverted_index.items() for pos in positions)
    return " ".join(word for _, word in indexed)


def _extract_arxiv_id(work: dict) -> str:
    """Find the arXiv ID for a work, if available.

    OpenAlex doesn't expose arXiv IDs directly. We scan the ``locations`` array for a location whose source is the arXiv
    repository, then extract the ID from the URL (e.g. ``/abs/2401.09417`` → ``2401.09417``). Falls back to checking
    ``ids.arxiv`` if present (newer API versions).
    """
    # Direct field (not always present)
    ids = work.get("ids") or {}
    if ids.get("arxiv"):
        return str(ids["arxiv"])

    # Scan locations for an arXiv-hosted version
    for loc in work.get("locations") or []:
        source = loc.get("source") or {}
        name = (source.get("display_name") or "").lower()
        if "arxiv" in name:
            url = loc.get("url") or ""
            if "/abs/" in url:
                tail = url.split("/abs/", 1)[1]
                # Strip version suffix
                if "v" in tail:
                    base, _, suffix = tail.rpartition("v")
                    if suffix.isdigit():
                        return base
                return tail
    return ""


def _extract_oa_pdf(work: dict) -> str:
    """Find the best open-access PDF URL for a work."""
    # Primary OA location
    oa = work.get("open_access") or {}
    oa_url = oa.get("oa_url") or ""
    if oa_url and oa_url.endswith(".pdf"):
        return oa_url

    # Scan best OA location
    best = work.get("best_oa_location") or {}
    pdf = best.get("pdf_url") or ""
    if pdf:
        return pdf

    # Fallback: scan all locations for a PDF
    for loc in work.get("locations") or []:
        if loc.get("is_oa"):
            pdf = loc.get("pdf_url") or ""
            if pdf:
                return pdf

    return ""


def _parse_work(work: dict) -> dict:
    """Turn one OpenAlex work object into a paper dict."""
    # Authors — OpenAlex stores them as authorships with position info
    authors: list[str] = []
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        name = author.get("display_name") or ""
        if name:
            authors.append(name)

    # Concepts — top 5 by score
    concepts: list[dict] = []
    for c in (work.get("concepts") or [])[:5]:
        concepts.append({"name": c.get("display_name", ""), "score": round(c.get("score", 0.0), 3), "level": c.get("level")})

    return {
        "id": work.get("id", ""),
        "title": work.get("title", "") or "",
        "authors": authors,
        "abstract": _reconstruct_abstract(work.get("abstract_inverted_index")),
        "published": (work.get("publication_date") or "")[:10],
        "cited_by_count": work.get("cited_by_count", 0),
        "doi": work.get("doi") or "",
        "arxiv_id": _extract_arxiv_id(work),
        "pdf_url": _extract_oa_pdf(work),
        "concepts": concepts,
        "related_works": (work.get("related_works") or [])[:10],
        "referenced_works_count": len(work.get("referenced_works") or []),
    }


def _build_filters(
    query: str, start_date: str | None, end_date: str | None, concept: str | None, cites: str | None
) -> list[str]:
    """Build the OpenAlex ``filter`` parameter.

    OpenAlex filters are comma-separated ``key:value`` pairs. We support:
    - ``title_and_abstract.search:`` for full-text search
    - ``from_publication_date:`` / ``to_publication_date:`` for date ranges
    - ``concepts.id:`` for concept filtering
    - ``cites:`` for reverse-citation lookup (find papers citing a work)
    """
    filters: list[str] = []

    if query:
        # OpenAlex handles multi-word search naturally — no quoting needed
        filters.append(f"title_and_abstract.search:{query}")

    if start_date:
        filters.append(f"from_publication_date:{start_date}")
    if end_date:
        filters.append(f"to_publication_date:{end_date}")

    if concept:
        # Accept either a concept ID (C123) or a display name
        if concept.startswith("C") and concept[1:].isdigit():
            filters.append(f"concepts.id:{concept}")
        else:
            filters.append(f"concepts.display_name.search:{concept}")

    if cites:
        # Strip the OpenAlex URL prefix if the user pasted a full URL
        work_id = cites
        if "openalex.org/" in work_id:
            work_id = work_id.rsplit("/", 1)[-1]
        filters.append(f"cites:{work_id}")

    return filters


def search(
    query: str = "",
    max_results: int = 20,
    sort_by: str = "relevance",
    start_date: str | None = None,
    end_date: str | None = None,
    concept: str | None = None,
    cites: str | None = None,
    email: str | None = None,
    group_by: str | None = None,
) -> dict[str, Any]:
    """Query OpenAlex and return structured results.

    Args:
        query: free-text topic, e.g. "efficient transformer attention". Leave empty when using ``cites`` for reverse-citation lookup.
        max_results: number of papers to return (clamped to 50).
        sort_by: "relevance" (default), "cited_by_count", or "publication_date".
        start_date: YYYY-MM-DD, inclusive.
        end_date: YYYY-MM-DD, inclusive.
        concept: concept ID (e.g. "C41008148") or display name to filter by.
        cites: OpenAlex work ID to find papers citing that work.
        email: email for the OpenAlex politeness pool.
        group_by: field to group results by (e.g. "primary_topic.id"). When set, returns group counts instead of paper listings.

    Returns:
        Dict with ``meta`` (total count), ``results`` (list of paper dicts or group counts), and ``group_by`` (if applicable).
    """
    if max_results <= 0:
        return {"meta": {"count": 0}, "results": []}
    max_results = min(max_results, MAX_RESULTS_UPPER_BOUND)

    filters = _build_filters(query, start_date, end_date, concept, cites)
    if not filters:
        raise ValueError("At least one of query, concept, or cites must be provided")

    mailto = email or os.environ.get("OPENALEX_EMAIL", DEFAULT_EMAIL)

    params: dict[str, Any] = {
        "filter": ",".join(filters),
        "per-page": max_results,
        "mailto": mailto,
    }

    if group_by:
        params["group_by"] = group_by
    else:
        # Map friendly sort names to OpenAlex API values
        sort_map = {
            "cited_by_count": "cited_by_count:desc",
            "relevance": "relevance_score:desc",
            "publication_date": "publication_date:desc",
        }
        params["sort"] = sort_map.get(sort_by, f"{sort_by}:desc")

    resp = requests.get(OPENALEX_ENDPOINT, params=params, timeout=DEFAULT_TIMEOUT_SECONDS)
    resp.raise_for_status()

    import json as _json

    data = _json.loads(resp.text)

    if group_by:
        return {"meta": data.get("meta", {}), "group_by": data.get("group_by", [])}

    results = [_parse_work(w) for w in data.get("results", [])]
    return {"meta": data.get("meta", {}), "results": results}


# --- CLI -------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Query the OpenAlex API and emit structured paper metadata as JSON. "
            "Supports relevance-sorted search, date filtering, reverse-citation lookup, and topic clustering."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python openalex_search.py "efficient transformer attention" --max-results 10\n'
            '  python openalex_search.py "diffusion models" --sort-by cited_by_count --start-date 2024-01-01\n'
            '  python openalex_search.py --cites W4403944333 --max-results 20\n'
            '  python openalex_search.py "transformer attention" --group-by primary_topic.id\n'
            '  python openalex_search.py "attention mechanism" --concept "Artificial intelligence"\n'
        ),
    )
    parser.add_argument("query", nargs="?", default="", help="free-text search topic (omit when using --cites)")
    parser.add_argument(
        "--max-results", type=int, default=20, help=f"number of papers to return (default: 20, max: {MAX_RESULTS_UPPER_BOUND})"
    )
    parser.add_argument(
        "--sort-by",
        default="relevance",
        choices=["cited_by_count", "relevance", "publication_date"],
        help="sort order (default: relevance — text-matching score)",
    )
    parser.add_argument("--start-date", default=None, help="earliest publication date, YYYY-MM-DD (inclusive)")
    parser.add_argument("--end-date", default=None, help="latest publication date, YYYY-MM-DD (inclusive)")
    parser.add_argument("--concept", default=None, help="filter by concept ID (e.g. C41008148) or display name")
    parser.add_argument(
        "--cites", default=None, help="OpenAlex work ID to find papers citing that work (e.g. W4403944333 or full URL)"
    )
    parser.add_argument(
        "--group-by",
        default=None,
        help="group results by a field (e.g. primary_topic.id) — returns cluster counts instead of paper listings",
    )
    parser.add_argument("--email", default=None, help="email for OpenAlex politeness pool (default: built-in)")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    try:
        result = search(
            query=args.query,
            max_results=args.max_results,
            sort_by=args.sort_by,
            start_date=args.start_date,
            end_date=args.end_date,
            concept=args.concept,
            cites=args.cites,
            email=args.email,
            group_by=args.group_by,
        )
    except Exception as exc:
        print(f"openalex_search.py: {exc}", file=sys.stderr)
        return 1

    import json as _json

    _json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
