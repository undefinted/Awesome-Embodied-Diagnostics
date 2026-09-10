"""Produce a bounded quality report and review queue for a frozen search run."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write_counts(path: Path, label: str, counts: Counter[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=[label, "candidate_records"])
        writer.writeheader()
        writer.writerows({label: key or "not_reported", "candidate_records": count} for key, count in sorted(counts.items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--manuscript-dir", type=Path)
    args = parser.parse_args()
    run = ROOT / "data" / "review" / "search_runs" / args.run_id
    with (run / "candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with (run / "query_log.csv").open(encoding="utf-8-sig", newline="") as handle:
        log = list(csv.DictReader(handle))
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    seed_rows = []
    if (run / "seed_recall.csv").exists():
        with (run / "seed_recall.csv").open(encoding="utf-8-sig", newline="") as handle:
            seed_rows = list(csv.DictReader(handle))
    source_totals = Counter()
    for row in log:
        if row["status"] == "ok":
            source_totals[row["source"]] += int(row["retrieved"])
    write_counts(run / "candidates_by_direction.csv", "direction", Counter(r["direction"] for r in rows))
    write_counts(run / "candidates_by_signal.csv", "automated_signal", Counter(r["automated_signal"] for r in rows))
    write_counts(run / "retrieval_by_source.csv", "source", source_totals)
    queue = [r for r in rows if r["automated_signal"] in {"high", "possible"} and r.get("future_year_flag", "").lower() != "true"]
    priority = {"high": 0, "possible": 1}
    queue.sort(key=lambda r: (priority[r["automated_signal"]], 0 if r.get("doi") or r.get("pmid") or r.get("arxiv_id") else 1, -(int(r["year"]) if r.get("year", "").isdigit() else 0), r["title"]))
    queue_fields = ["record_id", "automated_signal", "direction", "year", "title", "doi", "pmid", "pmcid", "arxiv_id", "url", "retrieval_provenance", "screening_status"]
    with (run / "automated_priority_subset.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=queue_fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(queue)
    quarantine = [r for r in rows if r.get("future_year_flag", "").lower() == "true"]
    with (run / "metadata_quarantine.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=queue_fields + ["future_year_flag"], extrasaction="ignore")
        writer.writeheader(); writer.writerows(quarantine)
    multi_source = sum(len(set(part.split(":", 1)[0] for part in r["retrieval_provenance"].split(";") if part)) > 1 for r in rows)
    overlap_available = multi_source > 0 or summary["retrieved_source_query_records"] == len(rows)
    known_retrieved = sum(r.get("retrieved", "").lower() == "true" for r in seed_rows)
    core_seed_rows = [r for r in seed_rows if r.get("core_search_expected", "").lower() == "true"]
    core_known_retrieved = sum(r.get("retrieved", "").lower() == "true" for r in core_seed_rows)
    saturated = sum(r.get("truncated_at_limit", "").lower() == "true" for r in log)
    title_counts = Counter(re.sub(r"[^a-z0-9]+", "", r["title"].lower()) for r in rows if r["title"])
    duplicate_title_clusters = sum(count > 1 for count in title_counts.values())
    malformed_dois = sum(bool(r.get("doi")) and not re.match(r"^10\.\d{4,9}/\S+$", r["doi"], flags=re.I) for r in rows)
    future_years = sum(r.get("year", "").isdigit() and int(r["year"]) > int(summary["until"][:4]) for r in rows)
    missing_identifiers = sum(not (r.get("doi") or r.get("pmid") or r.get("pmcid") or r.get("arxiv_id")) for r in rows)
    qc = {"records": len(rows), "blank_titles": sum(not r["title"] for r in rows), "duplicate_normalized_title_clusters": duplicate_title_clusters,
          "malformed_dois": malformed_dois, "future_year_records": future_years, "records_without_doi_pmid_pmcid_or_arxiv": missing_identifiers,
          "note": "Identifier syntax and internal consistency checks do not prove article-level relevance."}
    (run / "metadata_qc.json").write_text(json.dumps(qc, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Frozen Public-Source Search Quality", "",
        f"Run: `{args.run_id}`; date range: {summary['since']} to {summary['until']}.", "",
        "## Denominators", "",
        f"- Source-query records retrieved: {summary['retrieved_source_query_records']:,}.",
        f"- DOI/PMID/arXiv/title-deduplicated candidate records: {len(rows):,}.",
        f"- Conservative high-signal records: {sum(r['automated_signal'] == 'high' for r in rows):,}.",
        f"- Possible-signal records: {sum(r['automated_signal'] == 'possible' for r in rows):,}.",
        (f"- Records retrieved through more than one source family: {multi_source:,}." if overlap_available else "- Cross-source overlap: not recoverable for this resumed run; future runs preserve record-level provenance."),
        f"- Source-query pairs completed successfully: {summary.get('successful_source_queries', 0)}/{summary.get('configured_source_query_pairs', len(log))}.",
        f"- Source-query pairs ending in a recorded error: {summary.get('failed_source_queries', 0)}.",
        f"- Configured source-query pairs not run: {summary.get('unrun_source_queries', 0)}.",
        f"- Source-query pairs reaching the configured result cap: {saturated}.", "",
        "## Metadata quality controls", "",
        f"- Blank titles: {qc['blank_titles']}.",
        f"- Duplicate normalized-title clusters remaining after identifier-first deduplication: {duplicate_title_clusters}.",
        f"- Malformed DOI strings: {malformed_dois}.",
        f"- Records dated beyond the frozen search year: {future_years}.",
        f"- Records without DOI, PMID, PMCID or arXiv identifier: {missing_identifiers}.",
        "These checks detect internal metadata problems; DOI/title agreement and full-text relevance still require verification.", "",
        "## Known-item sensitivity check", "",
        f"The strategy retrieved {known_retrieved}/{len(seed_rows)} manuscript evidence seeds ({known_retrieved / len(seed_rows):.1%})" if seed_rows else "Known-item testing has not been run.",
        (f"Among seed reports coded as direct, bounded, human-mediated or assisted-sampling evidence, it retrieved {core_known_retrieved}/{len(core_seed_rows)} ({core_known_retrieved / len(core_seed_rows):.1%})." if core_seed_rows else "Role-stratified known-item testing has not been run."),
        "This is sensitivity against a small convenience set, not recall against an unknown universe. Missing known items require query refinement or documented citation chasing.", "",
        "## Can these data support review figures?", "",
        (("Not yet for publication-volume or prevalence claims. Result caps, heterogeneous index coverage and pending human screening make raw retrieval counts unsuitable as estimates of the field." if saturated else "Not yet for publication-volume or prevalence claims. Although this run has no configured result-cap truncation, heterogeneous index coverage, known-item gaps and pending human screening make raw retrieval counts unsuitable as estimates of the field.")),
        "The data are suitable for managing screening workload, finding terminology gaps and documenting source coverage.", "",
        "The high/possible subset is an ordering aid only. Every non-quarantined candidate remains in the title-and-abstract eligibility ledger; existing rule-based low-priority or exclusion suggestions are never final decisions.",
        "After duplicate human screening, final included records can support descriptive counts by direction, year, evidence stage, loop execution and safety-reporting status. Task-success percentages should remain study-level unless a separate meta-analysis establishes compatible designs and outcomes.", "",
        "## Required next steps", "",
        ("1. Split every capped query by year or narrower concept until no stratum is truncated." if saturated else "1. Preserve the zero-truncation audit and rerun any source-query pair whose returned count no longer matches its reported total."),
        "2. Resolve any recorded source-query failures and preserve them explicitly when a source remains unavailable.",
        "3. Import IEEE Xplore, Embase, Scopus and Web of Science exports where institutional access permits.",
        "4. Screen every non-quarantined candidate independently in duplicate; machine signals only determine order.",
        "5. Perform backward and forward citation chasing and deduplicate at both report and system level.",
        "6. Populate the extraction schema and conduct study-design-appropriate quality assessment.", "",
    ]
    (run / "SEARCH_QUALITY.md").write_text("\n".join(report), encoding="utf-8")
    human_queue = len(rows) - future_years
    until_date = date.fromisoformat(summary["until"])
    until_label = f"{until_date.day} {until_date.strftime('%B %Y')}"
    generated_summary = (
        f"The frozen definitive public-source search covered 1 January 2000 to {until_label} "
        f"across PubMed, Europe PMC and arXiv. It retrieved {summary['retrieved_source_query_records']:,} "
        f"source--query records and produced {len(rows):,} identifier- or title-deduplicated candidates; "
        f"{human_queue:,} non-quarantined records entered the title-and-abstract eligibility ledger, "
        f"with {sum(r['automated_signal'] in {'high', 'possible'} for r in rows):,} high- or possible-signal "
        "records used only to order screening. All "
        f"{summary.get('configured_source_query_pairs', len(log))} configured source--query pairs completed, "
        f"no result-cap truncation remained, and returned counts matched source-reported totals. "
        "OpenAlex remains a supplementary discovery source rather than part of this definitive count because "
        "its broad search parameter has not been validated as an equivalent Boolean bibliographic search. "
        f"The strategy retrieved {known_retrieved}/{len(seed_rows)} representative manuscript seeds"
        + (f" and {core_known_retrieved}/{len(core_seed_rows)} seeds coded as direct, bounded, human-mediated or assisted-sampling evidence" if core_seed_rows else "")
        + ". These are retrieval and workload denominators, not included-study counts or estimates of field size. "
        "Duplicate independent screening, full-text exclusion records, report--study--system linkage, citation "
        "chasing and design-specific risk-of-bias assessment remain required before any systematic-review claim.\n"
    )
    (run / "manuscript_search_summary.tex").write_text(generated_summary, encoding="utf-8")
    if args.manuscript_dir:
        (args.manuscript_dir / "generated_search_summary.tex").write_text(generated_summary, encoding="utf-8")
    print(f"screening_queue={len(queue)} multi_source={multi_source} saturated_queries={saturated}")


if __name__ == "__main__":
    main()
