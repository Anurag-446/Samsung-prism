"""Canonical semantic case signature generator for fast-path cache keying (M5-01)."""

from fixgraph.contracts.internal import CaseSignature, SymptomAtom
from fixgraph.data.fingerprints import compute_sha256_string


class CaseSignatureGenerator:
    def generate_signature(self, atom: SymptomAtom) -> CaseSignature:
        domains_sorted = sorted(set(atom.domains))
        symptoms_sorted = sorted(set(atom.symptoms))
        device_clean = atom.device.strip().lower()
        trigger_clean = (atom.trigger or "").strip().lower()

        # Build canonical signature string
        components = [
            f"device:{device_clean}",
            f"domains:{','.join(domains_sorted)}",
            f"symptoms:{','.join(symptoms_sorted)}",
            f"trigger:{trigger_clean}",
        ]
        canonical_str = "|".join(components)
        sig_hash = compute_sha256_string(canonical_str)

        return CaseSignature(
            version="v1",
            signature_hash=sig_hash,
            canonical_query=canonical_str,
            device=atom.device,
            domain_primary=domains_sorted[0] if domains_sorted else "general",
            symptoms_sorted=symptoms_sorted,
            trigger=atom.trigger,
        )
