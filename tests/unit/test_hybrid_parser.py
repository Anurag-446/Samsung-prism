"""Unit tests for Hybrid SymptomParser."""
from fixgraph.contracts.internal import NormalizedQuery
from fixgraph.query.symptom_parser import SymptomParser


def test_multi_symptom_hybrid_extraction():
    parser = SymptomParser() # uses mock provider
    q = NormalizedQuery(
        raw_query="screen flickers and battery drains fast after update",
        clean_query="screen flickers and battery drains fast after update",
        tokens=[]
    )
    atom = parser.extract_atoms(q, evidence_spans=[])
    assert "battery_drain" in atom.symptoms
    assert "display_issue" in atom.symptoms
    assert atom.trigger == "post_update" or atom.trigger == "post_system_update"

def test_user_constraints_preserved():
    parser = SymptomParser()
    q = NormalizedQuery(
        raw_query="battery drains fast but do not reset my phone",
        clean_query="battery drains fast but do not reset my phone",
        tokens=[]
    )
    atom = parser.extract_atoms(q, evidence_spans=[])
    assert "battery_drain" in atom.symptoms
    assert "reset" in atom.constraints.prohibited_actions

def test_completed_actions_preserved():
    parser = SymptomParser()
    q = NormalizedQuery(
        raw_query="wifi still fails, I already restarted the phone",
        clean_query="wifi still fails, I already restarted the phone",
        tokens=[]
    )
    atom = parser.extract_atoms(q, evidence_spans=[])
    assert "network_issue" in atom.symptoms or "wifi_disconnection" in atom.symptoms
    assert "restart" in atom.constraints.completed_actions
