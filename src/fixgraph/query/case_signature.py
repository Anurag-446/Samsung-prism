"""Canonical semantic case signature generator for fast-path cache keying (M5-01)."""

from fixgraph.contracts.internal import CaseSignature, SymptomAtom
from fixgraph.data.fingerprints import compute_sha256_string


class CaseSignatureGenerator:
    def generate_signature(self, atom: SymptomAtom) -> CaseSignature:
        domains_sorted = sorted(set(atom.domains))
        symptoms_sorted = sorted(set(atom.symptoms))
        negated_symptoms_sorted = sorted(set(atom.constraints.negated_symptoms))
        prohibited_actions_sorted = sorted(set(atom.constraints.prohibited_actions))
        completed_actions_sorted = sorted(set(atom.constraints.completed_actions))

        device_clean = atom.device.strip().lower()
        trigger_clean = (atom.trigger or "").strip().lower()

        # Build canonical signature string deterministically
        components = [
            f"device:{device_clean}",
            f"domains:{','.join(domains_sorted)}",
            f"symptoms:{','.join(symptoms_sorted)}",
            f"negated_symptoms:{','.join(negated_symptoms_sorted)}",
            f"trigger:{trigger_clean}",
            f"prohibited:{','.join(prohibited_actions_sorted)}",
            f"completed:{','.join(completed_actions_sorted)}",
        ]

        # Sort entities for deterministic canonical string
        for k, v in sorted(atom.entities.items()):
            components.append(f"entity_{k}:{v.strip().lower()}")

        canonical_str = "|".join(components)
        sig_hash = compute_sha256_string(canonical_str)

        return CaseSignature(
            signature_version="case-signature-v2",
            signature_hash=sig_hash,
            canonical_string=canonical_str,
            device_family=device_clean,
            domains=domains_sorted,
            symptoms=symptoms_sorted,
            negated_symptoms=negated_symptoms_sorted,
            trigger=trigger_clean if trigger_clean else None,
            prohibited_actions=prohibited_actions_sorted,
            completed_actions=completed_actions_sorted,
            entities=atom.entities
        )
