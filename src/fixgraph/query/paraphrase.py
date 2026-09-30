"""Query variation and paraphrase generator producing 8-10 distinct registers (M5-06)."""

from typing import List

from fixgraph.contracts.internal import SymptomAtom


class ParaphraseGenerator:
    def generate_variations(self, raw_query: str, atom: SymptomAtom) -> List[str]:
        query_clean = raw_query.strip()
        primary_domain = atom.domains[0] if atom.domains else "settings"
        symptom_str = atom.symptoms[0].replace("_", " ") if atom.symptoms else "issue"

        variations = [
            # 1. Formal / Technical
            f"How to resolve {symptom_str} in Galaxy {primary_domain}",
            # 2. Casual
            f"My Galaxy phone has {symptom_str} how do I fix it",
            # 3. Keyword-only
            f"Galaxy {primary_domain} {symptom_str} fix guide",
            # 4. Frustrated / Colloquial
            f"Why is {symptom_str} so bad on my phone help",
            # 5. Typo-inclusive
            f"Galaxiy {primary_domain} {symptom_str} not wrking",
            # 6. Step-seeking
            f"Steps to troubleshoot {symptom_str} in {primary_domain}",
            # 7. Action-oriented
            f"Configure {primary_domain} to fix {symptom_str}",
            # 8. Short phrase
            f"Fix {symptom_str} in {primary_domain} settings",
        ]

        if atom.trigger:
            variations.append(f"Fix {symptom_str} after {atom.trigger.replace('_', ' ')}")

        # Deduplicate and trim to exactly 8-10 items
        deduped = list(dict.fromkeys(variations))
        if len(deduped) < 8:
            for i in range(len(deduped), 8):
                deduped.append(f"{query_clean} troubleshooting option {i + 1}")

        return deduped[:10]
