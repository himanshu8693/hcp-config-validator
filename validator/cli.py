import click
from .parser import collect_configs
from .rules_engine import load_rules, run_rules_for_file
from .reporters import print_report

@click.command()
@click.argument("paths", nargs=-1, required=True)
@click.option("--rules", required=True, multiple=True, help="Path to rules YAML (can be repeated)")
@click.option("--output", type=click.Choice(["console","json","md"]), default="console")
@click.option("--fail-level", type=click.Choice(["info","warning","critical"]), default=None,
              help="Exit non-zero if rule with this severity or higher fails.")
def main(paths, rules, output, fail_level):
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
    # determine exit code

    if fail_level:
        order = {"info": 0, "warning": 1, "critical": 2}
        for entry in report:
            for r in entry["results"]:
                if (not r["passed"]) and (order[r["severity"]] >= order[fail_level]):
                    raise SystemExit(2)


if __name__ == "__main__":
    main()
