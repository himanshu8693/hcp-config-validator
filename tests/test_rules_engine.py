import pytest
from validator.rules_engine import evaluate_rule

def test_equals_operator():
    rule = {
        "id": "TEST-001",
        "jmespath": "foo.bar",
        "operator": "equals",
        "expected": 42
    }
    doc = {"foo": {"bar": 42}}
    result = evaluate_rule(rule, doc)
    assert result["passed"]

def test_absent_operator():
    rule = {
        "id": "TEST-002",
        "jmespath": "foo.baz",
        "operator": "absent"
    }
    doc = {"foo": {"bar": 42}}
    result = evaluate_rule(rule, doc)
    assert result["passed"]
