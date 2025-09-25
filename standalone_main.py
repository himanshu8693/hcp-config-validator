#!/usr/bin/env python3
"""
Standalone entry point for hcp-config-validator binary.

This script is REQUIRED for GitHub Actions PyInstaller builds.
It handles the imports properly for PyInstaller and serves as the
main entry point referenced in .github/workflows/build-release.yml

DO NOT REMOVE - Required for binary builds in CI/CD pipeline.
"""
import os
import sys
from pathlib import Path

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the main CLI
from validator.main import cli

if __name__ == "__main__":
    cli()