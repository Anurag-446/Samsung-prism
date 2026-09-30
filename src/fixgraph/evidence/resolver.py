"""Evidence segmentation and provenance tracking module (M3-05)."""

import re
from typing import List, Optional

from fixgraph.contracts.internal import EvidenceSpan


class EvidenceResolver:
    def segment_evidence(self, siis_response: Optional[str]) -> List[EvidenceSpan]:
        if not siis_response or not siis_response.strip():
            return []

        clean_text = siis_response.strip()
        # Split by sentence or double newline into evidence spans
        sentences = re.split(r"(?<=[.!?])\s+|\n+", clean_text)
        spans: List[EvidenceSpan] = []

        curr_offset = 0
        for idx, s in enumerate(sentences, start=1):
            sentence_clean = s.strip()
            if not sentence_clean:
                continue

            offset_start = clean_text.find(sentence_clean, curr_offset)
            if offset_start == -1:
                offset_start = curr_offset

            offset_end = offset_start + len(sentence_clean)
            curr_offset = offset_end

            spans.append(
                EvidenceSpan(
                    evidence_id=f"ev_{idx}",
                    source_offset_start=offset_start,
                    source_offset_end=offset_end,
                    text_content=sentence_clean,
                    source_type="siis",
                )
            )

        return spans
