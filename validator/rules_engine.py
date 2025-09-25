import yaml
import jmespath
import re

OPERATORS = {"exists", "equals", "in", "regex", "gt", "lt", "not_equals", "absent"}

def load_rules(path_or_list):
    rules = []
    if isinstance(path_or_list, (list,tuple)):
        for p in path_or_list:
            rules.extend(load_rules(p))
    else:
        with open(path_or_list, 'r') as f:
            data = yaml.safe_load(f)
            if isinstance(data, list):
                rules.extend(data)
            elif isinstance(data, dict) and "rules" in data:
                rules.extend(data["rules"])
    return rules

def evaluate_rule(rule, doc):
    expr = rule.get("jmespath")
    operator = rule.get("operator", "exists")
    expected = rule.get("expected")
    observed = None

    if expr:
        try:
            observed = jmespath.search(expr, doc)
        except Exception:
            observed = None

    # If observed is a list (e.g., multiple listeners), check all
    if isinstance(observed, list):
        # For 'exists', pass if all exist; for others, fail if any fail
        # Special case: flatten nested lists (e.g., JMESPath wildcards)
        flat = []
        for item in observed:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)
        observed = flat
        if operator == "regex":
            # Fail if any item matches regex
            passed = not any(_eval_single(operator, item, expected) for item in observed)
        elif operator == "exists":
            passed = all(_eval_single(operator, item, expected) for item in observed)
        elif operator == "absent":
            passed = all(_eval_single(operator, item, expected) for item in observed)
        else:
            passed = all(_eval_single(operator, item, expected) for item in observed)
    else:
        passed = _eval_single(operator, observed, expected, rule=rule)

    return {
        "id": rule.get("id"),
        "title": rule.get("title"),
        "severity": rule.get("severity", "info"),
        "passed": passed,
        "observed": observed,
        "message": rule.get("message"),
        "remediation": rule.get("remediation"),
        "reference": rule.get("reference")
    }

def _eval_single(operator, observed, expected, rule=None):
    # Special case for Vault TLS version string comparison
    def tls_version_to_num(v):
        if v is None:
            return 0  # Default to lowest version if None
        if isinstance(v, str) and v.startswith("tls"):
            return int(v.replace("tls", ""))
        return v if v is not None else 0
    if operator == "exists":
        return observed is not None
    elif operator == "absent":
        return observed is None
    elif operator == "equals":
        # For tls_min_version, compare as version
        if rule and rule.get("jmespath", "").endswith("tls_min_version"):
            return tls_version_to_num(observed) == tls_version_to_num(expected)
        return observed == expected
    elif operator == "not_equals":
        if rule and rule.get("jmespath", "").endswith("tls_min_version"):
            return tls_version_to_num(observed) != tls_version_to_num(expected)
        return observed != expected
    elif operator == "in":
        return observed in expected if observed is not None else False
    elif operator == "regex":
        # Only fail if a real match is found
        if observed is None:
            return False
        return bool(re.search(expected, str(observed)))
    elif operator == "gt":
        # For tls_min_version, compare as version
        if rule and rule.get("jmespath", "").endswith("tls_min_version"):
            return tls_version_to_num(observed) > tls_version_to_num(expected)
        try:
            return float(observed) > float(expected)
        except Exception:
            return False
    elif operator == "lt":
        if rule and rule.get("jmespath", "").endswith("tls_min_version"):
            return tls_version_to_num(observed) < tls_version_to_num(expected)
        try:
            return float(observed) < float(expected)
        except Exception:
            return False
    else:
        return False

def run_rules_for_file(rules, parsed_doc):
    results = []
    for r in rules:
        results.append(evaluate_rule(r, parsed_doc))
    return results
