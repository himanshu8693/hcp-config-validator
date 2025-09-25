# Contributing to hcp-config-validator

Thank you for your interest in contributing! This project thrives on community input and improvements.

## How to Contribute

- **Add new rules:** See the `README.md` for a full guide and template. Add your rule to the appropriate YAML file in `validator/rules/`.
- **Improve code:** Submit PRs for bug fixes, new features, or refactoring.
- **Suggest enhancements:** Open an issue to discuss new ideas or request features.

## Authoring Custom Rules

Each rule is a YAML object with these fields:
- `id`: Unique rule ID (e.g., VLT-051, CNS-031, NMD-031, COM-009)
- `title`: Short description of the rule
- `product`: `vault`, `consul`, `nomad`, or `all`
- `severity`: `info`, `warning`, or `critical`
- `jmespath`: JMESPath expression to extract the value from the config
- `operator`: One of `exists`, `absent`, `equals`, `not_equals`, `in`, `regex`, `gt`, `lt`
- `expected`: Value or list (if needed for the operator)
- `message`: Message shown if the rule fails
- `remediation`: How to fix the issue
- `reference`: (Optional) URL to official HashiCorp documentation

### Example Custom Rule

```yaml
- id: VLT-051
  title: "Vault telemetry sent to statsd"
  product: vault
  severity: info
  jmespath: "telemetry.statsd_address"
  operator: equals
  expected: "127.0.0.1:8125"
  message: "Vault telemetry is not sent to the expected statsd address."
  remediation: "Set telemetry.statsd_address to 127.0.0.1:8125 for local statsd collection."
  reference: "https://developer.hashicorp.com/vault/docs/configuration/telemetry"
```

### JMESPath Tips
- Use dot notation for nested fields: `listener[0].tls_disable`
- Use wildcards for arrays: `audit[*].type`
- Use `*` for all fields (for regex or secret scanning): `*`

### Operator Reference
- `exists`: Passes if the field exists
- `absent`: Passes if the field does not exist
- `equals`: Passes if the value equals `expected`
- `not_equals`: Passes if the value does not equal `expected`
- `in`: Passes if the value is in the `expected` list
- `regex`: Passes if the value matches the regex in `expected`
- `gt`/`lt`: Passes if the value is greater/less than `expected` (numeric or string)

## Submitting a Pull Request

1. Fork the repo and create your branch from `main`.
2. Add or update tests as appropriate.
3. Ensure your code passes linting and CI.
4. Open a PR and describe your changes.

## Code of Conduct

Be respectful and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) if present.

---

Happy contributing!
