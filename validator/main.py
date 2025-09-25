#!/usr/bin/env python3
"""
hcp-config-validator - HashiCorp Configuration Validator
A comprehensive tool for validating HashiCorp product configurations.
"""
import click
import os
import sys
from pathlib import Path

# Handle both standalone and module execution
try:
    from .parser import collect_configs
    from .rules_engine import load_rules, run_rules_for_file
    from .reporters import print_report
except ImportError:
    # When running as a standalone binary
    from parser import collect_configs
    from rules_engine import load_rules, run_rules_for_file
    from reporters import print_report


def get_rules_path():
    """Get the path to the rules directory, handling both development and binary environments."""
    # Try to get the rules path relative to this module
    current_dir = Path(__file__).parent
    rules_dir = current_dir / "rules"
    
    if rules_dir.exists():
        return rules_dir
    
    # If running as a binary, rules might be in a different location
    # PyInstaller creates a temporary folder and stores path in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        rules_dir = Path(sys._MEIPASS) / "validator" / "rules"
        if rules_dir.exists():
            return rules_dir
    
    # Fallback: look for rules directory in common locations
    possible_paths = [
        Path.cwd() / "validator" / "rules",
        Path.cwd() / "rules",
        current_dir.parent / "rules",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError("Rules directory not found. Please ensure the rules files are available.")


def load_product_rules(product):
    """Load rules for a specific product (common rules + product-specific rules)."""
    rules_dir = get_rules_path()
    all_rules = []
    
    # Always load common rules first
    common_rules_file = rules_dir / "common_rules.yaml"
    if common_rules_file.exists():
        print(f"[hcp-config-validator] Loading common rules: {common_rules_file}")
        all_rules.extend(load_rules(str(common_rules_file)))
    else:
        print(f"[hcp-config-validator] Warning: Common rules not found at {common_rules_file}")
    
    # Load product-specific rules
    product_rules_file = rules_dir / f"{product}_rules.yaml"
    if product_rules_file.exists():
        print(f"[hcp-config-validator] Loading {product} rules: {product_rules_file}")
        all_rules.extend(load_rules(str(product_rules_file)))
    else:
        print(f"[hcp-config-validator] Warning: {product} rules not found at {product_rules_file}")
        print(f"[hcp-config-validator] Continuing with common rules only...")
    
    return all_rules


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", is_flag=True, help="Show version information")
def cli(ctx, version):
    """HashiCorp Configuration Validator
    
    Validate HashiCorp product configurations against security and best practice rules.
    
    Usage:
        hcp-config-validator <product> --file <path>
        hcp-config-validator <product> --directory <path>
    
    Supported products: vault, consul, nomad
    """
    if version:
        click.echo("hcp-config-validator v1.0.0")
        return
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def create_product_command(product_name):
    """Create a click command for a specific product."""
    
    @click.command(name=product_name)
    @click.option("--file", "file_path", help="Path to a single configuration file")
    @click.option("--directory", "dir_path", help="Path to a directory containing configuration files")
    @click.option("--output", type=click.Choice(["console", "json", "md"]), default="console",
                  help="Output format for the validation report")
    @click.option("--fail-level", type=click.Choice(["info", "warning", "critical"]), default=None,
                  help="Exit non-zero if rule with this severity or higher fails")
    def product_command(file_path, dir_path, output, fail_level):
        f"""Validate {product_name.title()} configuration files."""
        
        # Validate input arguments
        if not file_path and not dir_path:
            click.echo(f"Error: Must specify either --file or --directory for {product_name} validation.")
            raise click.Abort()
        
        if file_path and dir_path:
            click.echo("Error: Cannot specify both --file and --directory. Choose one.")
            raise click.Abort()
        
        # Determine paths to validate
        if file_path:
            if not Path(file_path).exists():
                click.echo(f"Error: File not found: {file_path}")
                raise click.Abort()
            paths = [file_path]
        else:
            if not Path(dir_path).exists():
                click.echo(f"Error: Directory not found: {dir_path}")
                raise click.Abort()
            paths = [dir_path]
        
        print(f"[hcp-config-validator] Starting {product_name.title()} validation...")
        
        # Collect configuration files
        try:
            files = collect_configs(paths)
        except Exception as e:
            click.echo(f"Error parsing configuration files: {e}")
            raise click.Abort()
        
        if not files:
            print(f"[hcp-config-validator] No {product_name} config files found or parsed. Exiting.")
            return
        
        # Load product-specific rules
        try:
            all_rules = load_product_rules(product_name)
        except FileNotFoundError as e:
            click.echo(f"Error: {e}")
            raise click.Abort()
        
        if not all_rules:
            click.echo(f"Warning: No rules loaded for {product_name}. Check rules files.")
            return
        
        print(f"[hcp-config-validator] Loaded {len(all_rules)} rules for {product_name} validation")
        
        # Run validation
        report = []
        for path, parsed in files:
            results = run_rules_for_file(all_rules, parsed)
            report.append({"file": str(path), "results": results})
        
        # Print report
        print_report(report, output)
        print(f"[hcp-config-validator] {product_name.title()} validation complete.")
        
        # Determine exit code based on fail level
        if fail_level:
            severity_order = {"info": 0, "warning": 1, "critical": 2}
            for entry in report:
                for result in entry["results"]:
                    if (not result["passed"]) and (severity_order[result["severity"]] >= severity_order[fail_level]):
                        click.echo(f"Validation failed: Found {result['severity']} level issue(s)")
                        raise SystemExit(2)
    
    return product_command


# Add product commands
cli.add_command(create_product_command("vault"))
cli.add_command(create_product_command("consul"))
cli.add_command(create_product_command("nomad"))


# Add a generic validate command for backward compatibility
@cli.command()
@click.argument("paths", nargs=-1, required=True)
@click.option("--rules", required=True, multiple=True, help="Path to rules YAML (can be repeated)")
@click.option("--output", type=click.Choice(["console", "json", "md"]), default="console")
@click.option("--fail-level", type=click.Choice(["info", "warning", "critical"]), default=None,
              help="Exit non-zero if rule with this severity or higher fails.")
def validate(paths, rules, output, fail_level):
    """Generic validation command (backward compatibility)."""
    print("[hcp-config-validator] Starting validation...")
    files = collect_configs(paths)
    if not files:
        print("[hcp-config-validator] No config files found or parsed. Exiting.")
        return
    
    all_rules = []
    for r in rules:
        all_rules.extend(load_rules(r))
    
    report = []
    for path, parsed in files:
        results = run_rules_for_file(all_rules, parsed)
        report.append({"file": str(path), "results": results})
    
    print_report(report, output)
    print("[hcp-config-validator] Validation complete.")
    
    # Determine exit code
    if fail_level:
        severity_order = {"info": 0, "warning": 1, "critical": 2}
        for entry in report:
            for r in entry["results"]:
                if (not r["passed"]) and (severity_order[r["severity"]] >= severity_order[fail_level]):
                    raise SystemExit(2)


if __name__ == "__main__":
    cli()