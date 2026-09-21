"""URL leak hygiene validator enforcing zero external web URL leakage (P0-05)."""

import re
from typing import List
from fixgraph.contracts.internal import ValidationIssue


# Regex patterns matching web URLs, markdown links, HTML hrefs, and common obfuscations
URL_PATTERNS = [
    re.compile(r"https?://[^\s]+", re.IGNORECASE),
    re.compile(r"www\.[a-z0-9\-]+\.[a-z]{2,}", re.IGNORECASE),
    re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)", re.IGNORECASE),
    re.compile(r"href\s*=\s*['\"]?https?://", re.IGNORECASE),
    re.compile(r"h\s*t\s*t\s*p\s*s?\s*:\s*/\s*/", re.IGNORECASE),
    re.compile(r"http\[:\]//", re.IGNORECASE),
]


class URLLeakValidator:
    """Enforces zero web URL leakage in visible text fields of the troubleshooting plan."""

    def validate_text(self, text: str, field_name: str = "text") -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        if not text:
            return issues

        for pattern in URL_PATTERNS:
            match = pattern.search(text)
            if match:
                issues.append(
                    ValidationIssue(
                        code="URL_LEAK_DETECTED",
                        message=f"Forbidden web URL pattern '{match.group(0)}' detected in {field_name}",
                        field=field_name,
                        severity="ERROR",
                    )
                )
                break
        return issues
