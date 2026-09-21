"""Final plan compiler converting internal resolved actions to official Goal model (M4-04)."""

from typing import List
from fixgraph.contracts.internal import ResolvedAction, SymptomAtom
from fixgraph.contracts.public import (
    Action,
    BaseDeeplink,
    CategoryEnum,
    Goal,
    ResultTypes,
    StepGroup,
    ValidationDeeplink,
)
from fixgraph.query.paraphrase import ParaphraseGenerator


def _format_description(text: str) -> str:
    clean = text.strip()
    if not clean.lower().startswith("it will"):
        clean = f"It will {clean}"
    words = clean.split()
    if len(words) < 5:
        clean = f"{clean} on your device"
        words = clean.split()
    if len(words) > 7:
        clean = " ".join(words[:7])
    return clean


def _format_title(symptom_topic: str) -> str:
    words = symptom_topic.strip().split()
    if len(words) > 3:
        words = words[:3]
    elif len(words) < 2:
        words.append("issue")
    title_str = " ".join(words).capitalize()
    return title_str


class PlanCompiler:
    def __init__(self, paraphrase_gen: ParaphraseGenerator = None):
        self.paraphrase_gen = paraphrase_gen or ParaphraseGenerator()

    def compile(
        self, raw_query: str, atom: SymptomAtom, resolved_actions: List[ResolvedAction]
    ) -> Goal:
        primary_domain = atom.domains[0] if atom.domains else "Device"
        topic_title = primary_domain.capitalize()

        goal_phrase = f"Follow these steps to perform this {topic_title} Troubleshooting"
        title_phrase = _format_title(f"Fix {primary_domain.lower()}")

        compiled_actions: List[Action] = []
        for ra in resolved_actions:
            step_groups = [StepGroup(step=s) for s in ra.steps if s.strip()]
            if not step_groups:
                step_groups = [StepGroup(step=f"Open {ra.name} settings")]

            desc = _format_description(ra.description)
            cat_enum = CategoryEnum(ra.category)

            deeplink_obj = None
            if cat_enum != CategoryEnum.MANUAL and ra.exact_uri:
                deeplink_obj = ValidationDeeplink(
                    baseDeeplink=BaseDeeplink(uri=ra.exact_uri),
                    resultTypes=[ResultTypes(type="DEFAULT")],
                )

            compiled_actions.append(
                Action(
                    name=ra.name,
                    description=desc,
                    steps=step_groups,
                    category=cat_enum,
                    deeplink=deeplink_obj,
                )
            )

        query_vars = self.paraphrase_gen.generate_variations(raw_query, atom)

        # Calculate score from average action screen confidence
        conf_scores = [ra.screen_confidence for ra in resolved_actions]
        avg_score = sum(conf_scores) / len(conf_scores) if conf_scores else 0.85
        final_score = round(min(max(avg_score, 0.5), 1.0), 2)

        return Goal(
            goal=goal_phrase,
            title=title_phrase,
            score=final_score,
            actions=compiled_actions,
            query_variations=query_vars,
        )
