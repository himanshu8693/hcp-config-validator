import json
from rich.console import Console
from rich.table import Table

console = Console()

def print_report(report, format_="console"):
    print("[hcp-config-validator] Generating report...")
    if format_ == "json":
        print(json.dumps(report, indent=2))
        return
    if not report or all(all(r["passed"] for r in file_res["results"]) for file_res in report):
        console.print("[green]No issues found. All checks passed![/green]")
        return
    
    for file_res in report:
        # Calculate summary statistics
        results = file_res["results"]
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r["passed"])
        failed_rules = total_rules - passed_rules
        
        # Count by severity
        critical_failed = sum(1 for r in results if not r["passed"] and r["severity"] == "critical")
        warning_failed = sum(1 for r in results if not r["passed"] and r["severity"] == "warning")
        info_failed = sum(1 for r in results if not r["passed"] and r["severity"] == "info")
        
        # Print summary
        console.print(f"\n[bold]Summary for {file_res['file']}:[/bold]")
        console.print(f"Total rules: {total_rules} | Passed: [green]{passed_rules}[/green] | Failed: [red]{failed_rules}[/red]")
        if failed_rules > 0:
            console.print(f"Failed by severity: Critical: [red]{critical_failed}[/red] | Warning: [yellow]{warning_failed}[/yellow] | Info: [blue]{info_failed}[/blue]")
        console.print()
        
        table = Table(
            title=f"Config checks: {file_res['file']}", 
            show_header=True, 
            header_style="bold magenta",
            show_lines=True,
            row_styles=["none", "dim"],
            border_style="bright_blue",
            title_style="bold cyan",
            caption_style="italic",
            expand=True
        )
        table.add_column("ID", style="cyan", width=10, no_wrap=True)
        table.add_column("Title", style="bold", min_width=20, ratio=2)
        table.add_column("Severity", style="yellow", width=10, justify="center", no_wrap=True)
        table.add_column("Passed", style="green", width=8, justify="center", no_wrap=True)
        table.add_column("Message", style="white", min_width=30, ratio=3)
        table.add_column("Remediation", style="bright_white", min_width=30, ratio=3)
        table.add_column("Reference", style="dim blue", min_width=25, ratio=2)
        for r in file_res["results"]:
            # Color-code severity and pass/fail status
            severity_color = {
                "critical": "[red]CRITICAL[/red]",
                "warning": "[yellow]WARNING[/yellow]", 
                "info": "[blue]INFO[/blue]"
            }.get(r["severity"], r["severity"])
            
            pass_status = "[green]✔[/green]" if r["passed"] else "[red]✖[/red]"
            
            table.add_row(
                r["id"] or "-",
                r.get("title") or "-",
                severity_color,
                pass_status,
                r.get("message") or "",
                r.get("remediation") or "",
                r.get("reference") or "-"
            )
        console.print(table)
    print("[hcp-config-validator] Report generation complete.")
