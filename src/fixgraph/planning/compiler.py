"""Final plan compiler converting internal resolved actions to official Goal model (M4-04)."""

from typing import List

from fixgraph.contracts.internal import ResolvedAction, SymptomAtom
from fixgraph.contracts.public import (
    Action,
    Deeplink,
    actionCategory,
    Goal,
    ResultTypes,
    Condition,
    StepGroup,
    ValidationDeepLink,
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
        self, raw_query: str, atom: SymptomAtom, resolved_actions: List[ResolvedAction], catalog=None
    ) -> Goal:
        primary_domain = atom.domains[0] if atom.domains else "Device"
        topic_title = primary_domain.capitalize()

        goal_phrase = f"Follow these steps to perform this {topic_title} Troubleshooting"
        title_phrase = _format_title(f"Fix {primary_domain.lower()}")

        compiled_actions: List[Action] = []
        
        for ra in resolved_actions:
            cat_enum = actionCategory(ra.category)
            
            actionable_dl = None
            validation_dl = None
            
            if cat_enum != actionCategory.manual and ra.exact_uri and catalog:
                record = catalog.get_by_id(ra.catalog_record_id) if ra.catalog_record_id else None
                if record:
                    # Construct actionableDeeplink
                    actionable_dl = Deeplink(
                        deeplink=record.uri,
                        description=record.description,
                        message=record.message,
                        classes=record.classes if hasattr(record, 'classes') and record.classes else None,
                        originalType=record.original_type
                    )
                    # Construct validationDeeplink if it exists in the catalog record
                    if hasattr(record, 'validation') and record.validation:
                        val = record.validation
                        result_type = val.get("resultType")
                        val_res = ResultTypes(result_type) if result_type else None
                        
                        cond = val.get("condition")
                        val_cond = Condition(cond) if cond else None
                        
                        validation_dl = ValidationDeepLink(
                            deeplink=val.get("deeplink", ""),
                            key=val.get("key", ""),
                            resultType=val_res,
                            condition=val_cond,
                            value=val.get("value")
                        )

            # Map the exact format of StepGroup from the official schema
            # Official Schema: StepGroup(steps: List[str], validationDeeplink, actionableDeeplink)
            step_groups = [
                StepGroup(
                    steps=[s.strip() for s in ra.steps if s.strip()],
                    validationDeeplink=validation_dl,
                    actionableDeeplink=actionable_dl
                )
            ]
            if not step_groups[0].steps:
                step_groups[0].steps = [f"Open {ra.name} settings"]

            desc = _format_description(ra.description)

            compiled_actions.append(
                Action(
                    actionName=ra.name,
                    description=desc,
                    stepGroups=step_groups,
                    category=cat_enum,
                )
            )

        # Calculate score from average action screen confidence
        conf_scores = [ra.screen_confidence for ra in resolved_actions]
        avg_score = sum(conf_scores) / len(conf_scores) if conf_scores else 0.85
        final_score = round(min(max(avg_score, 0.5), 1.0), 2)

        return Goal(
            goal=goal_phrase,
            title=title_phrase,
            score=final_score,
            actions=compiled_actions,
        )
