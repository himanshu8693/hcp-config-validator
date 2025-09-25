# HCP Config Validator

A comprehensive static configuration validator for HashiCorp Vault, Consul, and Nomad. Detects risky parameters, insecure defaults, and best-practice violations in HCL, JSON, YAML, and TOML config files.

## Features
- 🔒 **172 Security Rules** across Vault, Consul, and Nomad
- 🚀 **Platform-Agnostic Binaries** for Windows, Linux, and macOS
- 📋 **Multiple Output Formats** (Console, JSON, Markdown)
- ⚡ **GitHub Actions Integration** with automated binary releases
- 🔧 **Extensible YAML-Based Rules** for custom validation
- 📊 **Rich Terminal Output** with enhanced table formatting

## Quick Start

### Download Pre-built Binaries

Download the latest release for your platform from the [GitHub Releases](../../releases) page:

- **Linux (x64)**: `hcp-config-validator-linux-amd64`
- **Windows (x64)**: `hcp-config-validator-windows-amd64.exe`
- **macOS (Intel)**: `hcp-config-validator-darwin-amd64`
- **macOS (Apple Silicon)**: `hcp-config-validator-darwin-arm64`

### Usage

```bash
# Make executable (Linux/macOS)
chmod +x hcp-config-validator-*

# Validate Vault configuration
./hcp-config-validator vault --file vault.json

# Validate Consul configuration directory
./hcp-config-validator consul --directory /path/to/consul/configs

# Validate Nomad configuration with JSON output
./hcp-config-validator nomad --file nomad.hcl --output json

# Validate with specific fail level
./hcp-config-validator vault --file vault.hcl --fail-level warning
```

### Development Setup

```bash
git clone <your-repo-url>
cd hcp-config-validator
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Test the CLI
python -m validator.main vault --file examples/vault.json
```

## Example Output

```
[hcp-config-validator] Starting Vault validation...
[hcp-config-validator] Loaded 92 rules for vault validation

Summary for vault.json:
Total rules: 92 | Passed: 45 | Failed: 47
Failed by severity: Critical: 12 | Warning: 28 | Info: 7

                             Config checks: vault.json                              
┏━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ ID         ┃ Title    ┃  Severity  ┃  Passed  ┃ Message      ┃ Remediation  ┃ Refere… ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ VLT-001    │ Storage  │  CRITICAL  │    ✖     │ Vault        │ Use raft or  │ https:… │
│            │ backend  │            │          │ storage type │ consul       │         │
│            │ not      │            │          │ is 'file'    │ storage for  │         │
│            │ 'file'   │            │          │ (not HA).    │ HA.          │         │
│ VLT-002    │ TLS      │  CRITICAL  │    ✖     │ TLS disabled │ Enable TLS   │ https:… │
│            │ enabled  │            │          │ on listener. │ for all      │         │
│            │ on all   │            │          │              │ listeners.   │         │
│            │ listene… │            │          │              │              │         │
└────────────┴──────────┴────────────┴──────────┴──────────────┴──────────────┴─────────┘
```

## Supported Products & Rules Coverage

### Rule Categories
- **Common Rules (32)**: Security, compliance, operational best practices
- **Vault Rules (60)**: Storage, listeners, audit, auth methods, policies, enterprise
- **Consul Rules (40)**: ACLs, gossip encryption, service mesh, enterprise features  
- **Nomad Rules (40)**: Workload identity, security, audit, enterprise features

### Total: 172 Validation Rules

## Authoring Custom Rules

You can easily add your own rules to extend the validator for your use case or contribute to the community rulesets.

### Rule Structure
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

Suppose you want to ensure Vault's telemetry is enabled and sent to a specific statsd address:

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

### Adding Your Rule
1. Open the relevant rules YAML file (e.g., `vault_rules.yaml`)
2. Add your rule at the end (or wherever you like)
3. Save and re-run the validator

### Testing Your Rule
- Create a sample config that should trigger the rule
- Run the validator and check the output

### Need Help?
Open an issue or PR, or see the examples in the `validator/rules/` directory for inspiration.

## CI/CD Integration

### GitHub Actions

This repository includes comprehensive GitHub Actions workflows:

#### Automated Binary Builds
- **Workflow**: `.github/workflows/build-release.yml`
- **Triggers**: Push to main, tags, manual dispatch
- **Platforms**: Linux (x64), Windows (x64), macOS (Intel + Apple Silicon)
- **Artifacts**: Platform-specific binaries uploaded as artifacts

#### Automated Releases
- **Trigger**: Git tags matching `v*` (e.g., `v1.0.0`)
- **Process**: 
  1. Builds binaries for all platforms
  2. Creates GitHub release with changelog
  3. Uploads binaries as release assets
  4. Generates download instructions

#### Creating a Release
```bash
# Tag and push for automated release
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will:
# - Build binaries for all platforms  
# - Create release with binaries
# - Generate changelog from commits
```

#### Using in Your GitHub Actions
```yaml
name: Validate Configs
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download validator
        run: |
          wget -O hcp-config-validator \
            https://github.com/your-username/hcp-config-validator/releases/latest/download/hcp-config-validator-linux-amd64
          chmod +x hcp-config-validator
          
      - name: Validate Vault configs
        run: ./hcp-config-validator vault --directory ./vault-configs --fail-level critical
```

### Local Development

#### Running Tests
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run test suite
python -m pytest tests/ -v

# Test CLI commands
python -m validator.main vault --file examples/vault.json
python -m validator.main consul --directory examples/consul/
python -m validator.main nomad --file examples/nomad.hcl
```

#### Building Locally (Optional)
```bash
# Install PyInstaller
pip install pyinstaller

# Build binary
pyinstaller --onefile --name hcp-config-validator \
  --add-data "validator/rules:validator/rules" \
  --hidden-import validator.rules_engine \
  --hidden-import validator.reporters \
  --hidden-import validator.main \
  standalone_main.py

# Test local binary
./dist/hcp-config-validator vault --file examples/vault.json
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add your changes and tests
4. Ensure tests pass (`python -m pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)  
7. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings for new functions and classes
- Update tests for new features

## License
MIT - See [LICENSE](LICENSE) file for details.
