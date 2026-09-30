"""Query normalizer for domain alias mapping, whitespace cleanup, and slang handling (M3-01)."""

import re
import unicodedata
from typing import List

from fixgraph.contracts.internal import NormalizedQuery

DOMAIN_ALIASES = {
    "wifi": "wi-fi",
    "wlan": "wi-fi",
    "bt": "bluetooth",
    "blue tooth": "bluetooth",
    "earbuds": "bluetooth",
    "gps": "location",
    "location service": "location",
    "battery drain": "battery protection",
    "power save": "battery protection",
    "fast charge": "battery protection",
    "darkmode": "display",
    "brightness": "display",
    "refresh rate": "display",
    "network reset": "reset mobile network settings",
}


class QueryNormalizer:
    def normalize(self, raw_query: str) -> NormalizedQuery:
        if not raw_query:
            return NormalizedQuery(raw_query="", clean_query="", tokens=[])

        # Unicode normalization (NFKD)
        normalized = unicodedata.normalize("NFKD", raw_query)

        # Casing and whitespace cleanup
        clean = normalized.lower().strip()
        clean = re.sub(r"\s+", " ", clean)

        # Apply domain alias mapping
        domain_tags: List[str] = []
        for alias, target in DOMAIN_ALIASES.items():
            if alias in clean:
                domain_tags.append(target)

        # Extract clean tokens
        tokens = [t for t in re.sub(r"[^\w\s]", " ", clean).split() if t]

        # Detect Galaxy device
        detected_device = "Galaxy"
        if "s24" in clean or "s23" in clean or "fold" in clean or "flip" in clean or "tab" in clean:
            detected_device = "Galaxy Flagship"

        return NormalizedQuery(
            raw_query=raw_query,
            clean_query=clean,
            tokens=tokens,
            detected_device=detected_device,
            domain_tags=list(set(domain_tags)),
        )
