"""Small JSON HTTP wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import requests


@dataclass
class JsonHttpClient:
    session: requests.Session

    def fetch_json(self, url: str, *, referer: str) -> Dict[str, object]:
        response = self.session.get(
            url,
            headers={
                "Referer": referer,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/plain, */*",
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
