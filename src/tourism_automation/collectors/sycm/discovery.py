"""Discovery helpers for SYCM network traffic."""

from __future__ import annotations

from typing import Dict, List
from urllib.parse import parse_qsl, urlparse


def discover_sycm_json_endpoints(net_output: str) -> List[Dict[str, object]]:
    seen = {}
    for line in net_output.splitlines():
        url = _extract_url(line)
        if not url or "sycm.taobao.com" not in url or ".json" not in url:
            continue
        parsed = urlparse(url)
        path = parsed.path
        query_keys = sorted({key for key, _ in parse_qsl(parsed.query) if key not in {"_", "token"}})
        seen[path] = {
            "path": path,
            "query_keys": query_keys,
            "url": url,
        }
    return [seen[path] for path in sorted(seen)]


def _extract_url(line: str) -> str:
    parts = line.split()
    for part in reversed(parts):
        if part.startswith("http://") or part.startswith("https://"):
            return part
    return ""
