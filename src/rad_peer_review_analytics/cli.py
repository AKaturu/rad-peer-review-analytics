from __future__ import annotations

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from rad_peer_review_analytics.analytics import AnalyticsEngine
from rad_peer_review_analytics.exporter import (
    export_report_csv,
    export_report_json,
    export_reviews_csv,
)
from rad_peer_review_analytics.importer import import_csv_file
from rad_peer_review_analytics.models import AnalyticsReport, PeerReview, Reviewer
from rad_peer_review_analytics.scoring import is_discrepant, is_major_discrepant
from rad_peer_review_analytics.synthetic import generate_demo_data

app = typer.Typer(
    name="rad-peer-review-analytics",
    help="Radiology peer review tracking, scoring, and analytics",
)
console = Console()
err_console = Console(stderr=True)

_reviews: list[PeerReview] = []
_reviewers: dict[str, Reviewer] = {}
_engine = AnalyticsEngine()


def _ensure_data() -> bool:
    if not _reviews:
        err_console.print("[yellow]No review data loaded. Use 'demo' or 'import' first.[/yellow]")
        return False
    return True


@app.callback()
def _main() -> None:
    pass


@app.command()
def demo(
    reviewers: int = typer.Option(8, "--reviewers", "-r", help="Number of reviewers"),
    reviews: int = typer.Option(100, "--reviews", "-n", help="Number of reviews"),
    system: str = typer.Option(
        "radpeer", "--system", "-s", help="Score system (radpeer or standard)"
    ),
    load: bool = typer.Option(
        True, "--load/--no-load", help="Load generated data into engine"
    ),
) -> None:
    """Generate synthetic peer review data for demonstration."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Generating demo data...", total=None)
        reviewers_list, reviews_list = generate_demo_data(
            reviewer_count=reviewers, review_count=reviews, score_system=system
        )

    global _reviews, _reviewers, _engine
    if load:
        _reviews = reviews_list
        _reviewers = {r.reviewer_id: r for r in reviewers_list}
        _engine.load(_reviews, list(_reviewers.values()))
        console.print(
            f"[green]Loaded {len(reviews_list)} reviews, "
            f"{len(reviewers_list)} reviewers[/green]"
        )
    else:
        console.print(
            f"[green]Generated {len(reviews_list)} reviews, "
            f"{len(reviewers_list)} reviewers[/green]"
        )

    _print_summary(reviews_list, reviewers_list)


@app.command()
def import_reviews(
    file: str = typer.Argument(..., help="CSV file to import"),
) -> None:
    """Import peer review data from CSV."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Importing reviews...", total=None)
        result = import_csv_file(file)

    global _reviews, _engine
    _reviews = result.rows
    _engine.load(_reviews)

    console.print(
        f"[green]Imported {len(result.rows)} reviews"
        + (f", skipped {result.skipped}" if result.skipped else "")
        + "[/green]"
    )

    for err in result.errors:
        err_console.print(f"[red]{err}[/red]")

    _print_summary(_reviews)


@app.command()
def analyze() -> None:
    """Generate analytics report from loaded data."""
    if not _ensure_data():
        raise typer.Exit(1)

    report = _engine.generate_report()
    _display_report(report)


@app.command()
def report(
    output: str | None = typer.Option(
        None, "--output", "-o", help="Export report CSV prefix"
    ),
    json_output: str | None = typer.Option(
        None, "--json", "-j", help="Export report to JSON"
    ),
) -> None:
    """Generate and display/export analytics report."""
    if not _ensure_data():
        raise typer.Exit(1)

    report = _engine.generate_report()
    _display_report(report)

    if output:
        export_report_csv(report, output)
        console.print(f"[green]Report CSV files exported to {output}_*.csv[/green]")
    if json_output:
        export_report_json(report, json_output)
        console.print(f"[green]Report JSON exported to {json_output}[/green]")


@app.command()
def reviewers() -> None:
    """List all reviewers with their stats."""
    if not _ensure_data():
        raise typer.Exit(1)

    report = _engine.generate_report()

    table = Table(title="Reviewer Statistics")
    table.add_column("Reviewer")
    table.add_column("Group")
    table.add_column("Total")
    table.add_column("Agreement", justify="right")
    table.add_column("Major Disc.", justify="right")
    table.add_column("Avg Score", justify="right")
    table.add_column("Trend")

    for rs in report.reviewer_stats:
        name = rs.name or rs.reviewer_id
        ag_pct = f"{rs.agreement_rate:.0%}"
        md_pct = f"{rs.major_discrepancy_rate:.0%}"
        trend_style = {
            "improving": "green",
            "declining": "red",
            "stable": "yellow",
        }.get(rs.trend_direction, "white")

        table.add_row(
            name,
            rs.group_name,
            str(rs.total_reviews),
            ag_pct,
            md_pct,
            f"{rs.avg_score:.3f}",
            f"[{trend_style}]{rs.trend_direction}[/{trend_style}]",
        )

    console.print(table)


@app.command()
def modalities() -> None:
    """Show modality-level stats."""
    if not _ensure_data():
        raise typer.Exit(1)

    report = _engine.generate_report()

    table = Table(title="Modality Statistics")
    table.add_column("Modality")
    table.add_column("Reviews")
    table.add_column("Agreement", justify="right")
    table.add_column("Major Disc.", justify="right")
    table.add_column("Avg Score", justify="right")

    for ms in report.modality_stats:
        table.add_row(
            ms.modality,
            str(ms.total_reviews),
            f"{ms.agreement_rate:.0%}",
            f"{ms.major_discrepancy_rate:.0%}",
            f"{ms.avg_score:.3f}",
        )

    console.print(table)


@app.command()
def trends() -> None:
    """Show monthly trend data."""
    if not _ensure_data():
        raise typer.Exit(1)

    report = _engine.generate_report()

    table = Table(title="Monthly Trends")
    table.add_column("Month")
    table.add_column("Reviews")
    table.add_column("Agreements")
    table.add_column("Agreement Rate", justify="right")
    table.add_column("Major Disc.", justify="right")

    for mt in report.monthly_trends:
        table.add_row(
            mt.year_month,
            str(mt.total_reviews),
            str(mt.agreement_count),
            f"{mt.agreement_rate:.0%}",
            str(mt.major_discrepancy_count),
        )

    console.print(table)

    if report.top_discrepant_modalities:
        console.print(
            f"\n[yellow]Top discrepant modalities:[/yellow] "
            f"{', '.join(report.top_discrepant_modalities)}"
        )


@app.command()
def export(
    path: str = typer.Argument(..., help="Output CSV path"),
) -> None:
    """Export loaded reviews to CSV."""
    if not _ensure_data():
        raise typer.Exit(1)

    export_reviews_csv(_reviews, path)
    console.print(f"[green]Exported {len(_reviews)} reviews to {path}[/green]")


def _print_summary(reviews: list[PeerReview], reviewers: list[Reviewer] | None = None) -> None:
    total = len(reviews)
    disc = sum(1 for r in reviews if is_discrepant(r.score, r.score_system))
    major = sum(1 for r in reviews if is_major_discrepant(r.score, r.score_system))
    unique_r_ids = len({r.reviewer_id for r in reviews if r.reviewer_id})

    console.print(
        f"[bold]Summary:[/bold] {total} reviews, {unique_r_ids} reviewers, "
        f"{total - disc} agreements ({((total - disc) / total * 100) if total else 0:.0f}%), "
        f"{major} major discrepancies ({major / total * 100 if total else 0:.0f}%)"
    )


def _display_report(report: AnalyticsReport) -> None:
    console.print("[bold]Peer Review Analytics Report[/bold]")
    console.print(f"Period: {report.date_range or 'N/A'}")
    console.print(
        f"Reviews: {report.total_reviews} | Reviewers: {report.total_reviewers}\n"
    )

    console.print(
        f"Overall Agreement Rate: [green]{report.overall_agreement_rate:.1%}[/green]"
    )
    console.print(
        f"Major Discrepancy Rate: [red]{report.overall_major_discrepancy_rate:.1%}[/red]"
    )
    console.print(f"Average Score: {report.overall_avg_score:.3f}\n")

    if report.reviewer_stats:
        table = Table(title="Top Reviewer Stats")
        table.add_column("Reviewer")
        table.add_column("Reviews")
        table.add_column("Agreement")
        table.add_column("Major Disc.")
        table.add_column("Trend")

        for rs in sorted(
            report.reviewer_stats, key=lambda x: x.major_discrepancy_rate, reverse=True
        )[:10]:
            name = rs.name or rs.reviewer_id
            trend_style = {
                "improving": "green",
                "declining": "red",
                "stable": "yellow",
            }.get(rs.trend_direction, "white")
            table.add_row(
                name,
                str(rs.total_reviews),
                f"{rs.agreement_rate:.0%}",
                f"{rs.major_discrepancy_rate:.0%}",
                f"[{trend_style}]{rs.trend_direction}[/{trend_style}]",
            )
        console.print(table)

    if report.top_discrepant_modalities:
        console.print(
            f"\n[yellow]Highest discrepancy modalities:[/yellow] "
            f"{', '.join(report.top_discrepant_modalities)}"
        )


if __name__ == "__main__":
    app()
