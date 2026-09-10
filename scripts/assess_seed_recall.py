"""Check whether the public search retrieves known manuscript evidence seeds."""
from __future__ import annotations

import argparse
import csv
import re
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "review" / "manuscript_evidence_seed.csv"
CODING = ROOT / "data" / "review" / "evidence_coding.csv"
CORE_SEARCH_ROLES = {
    "direct_embodied_diagnostic",
    "bounded_embodied_acquisition",
    "human_mediated_embodied_diagnostic",
    "assisted_sampling_evidence",
}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def doi_from_url(url: str) -> str:
    match = re.search(r"doi\.org/(10\.[^?#]+)", url or "", flags=re.I)
    return match.group(1).lower().rstrip(".,; ") if match else ""


def pmid_from_url(url: str) -> str:
    match = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url or "", flags=re.I)
    return match.group(1) if match else ""


def pmcid_from_url(url: str) -> str:
    match = re.search(r"PMC\d+", url or "", flags=re.I)
    return match.group(0).upper() if match else ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run = ROOT / "data" / "review" / "search_runs" / args.run_id
    with SEED.open(encoding="utf-8-sig", newline="") as handle:
        seeds = list(csv.DictReader(handle))
    with CODING.open(encoding="utf-8-sig", newline="") as handle:
        coding = {row["study"]: row for row in csv.DictReader(handle)}
    with (run / "candidates.csv").open(encoding="utf-8-sig", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    by_doi = {row["doi"].lower(): row for row in candidates if row.get("doi")}
    by_pmid = {row["pmid"]: row for row in candidates if row.get("pmid")}
    by_pmcid = {row["pmcid"].upper(): row for row in candidates if row.get("pmcid")}
    candidate_titles = [(norm(row["title"]), row) for row in candidates]
    rows = []
    for seed in seeds:
        doi, pmid, pmcid = doi_from_url(seed["public_url"]), pmid_from_url(seed["public_url"]), pmcid_from_url(seed["public_url"])
        match, method, similarity = None, "", 0.0
        if doi and doi in by_doi:
            match, method, similarity = by_doi[doi], "doi", 1.0
        elif pmid and pmid in by_pmid:
            match, method, similarity = by_pmid[pmid], "pmid", 1.0
        elif pmcid and pmcid in by_pmcid:
            match, method, similarity = by_pmcid[pmcid], "pmcid", 1.0
        else:
            target = norm(seed["study"])
            if target:
                similarity, match = max(
                    ((1.0 if len(target) >= 10 and (target in title or title in target) else SequenceMatcher(None, target, title).ratio(), row) for title, row in candidate_titles),
                    key=lambda pair: pair[0],
                )
                if similarity >= 0.82:
                    method = "normalized_title_similarity"
                else:
                    match = None
        role = coding[seed["study"]]["evidence_role"]
        rows.append({"seed_study": seed["study"], "seed_domain": seed["domain"], "evidence_role": role,
                     "core_search_expected": role in CORE_SEARCH_ROLES, "seed_url": seed["public_url"],
                     "retrieved": bool(match), "match_method": method, "title_similarity": round(similarity, 3),
                     "matched_record_id": match["record_id"] if match else "", "matched_title": match["title"] if match else "",
                     "retrieval_provenance": match["retrieval_provenance"] if match else ""})
    with (run / "seed_recall.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    retrieved = sum(row["retrieved"] for row in rows)
    core_rows = [row for row in rows if row["core_search_expected"]]
    core_retrieved = sum(row["retrieved"] for row in core_rows)
    text = ["# Known-seed retrieval check", "", f"- Denominator: {len(rows)} manuscript evidence-seed reports.",
            f"- Retrieved by the public-source strategy: {retrieved}/{len(rows)} ({retrieved / len(rows):.1%}).",
            f"- Core/bounded/human-mediated/assisted-sampling seed reports retrieved: {core_retrieved}/{len(core_rows)} ({core_retrieved / len(core_rows):.1%}).",
            f"- Not retrieved: {len(rows) - retrieved}.", "",
            "The role-stratified denominator was defined from the reviewer coding. Technical precedents and nonadaptive comparators remain visible but are not treated as expected core-search targets.",
            "This is a sensitivity check against a small, non-random known set. It is not an estimate of recall for the unknown full literature.", "",
            "Missing seeds should trigger query refinement or citation chasing; they must not be silently added to the numerator.", ""]
    (run / "SEED_RECALL.md").write_text("\n".join(text), encoding="utf-8")
    print(f"known_seed_retrieval={retrieved}/{len(rows)} ({retrieved / len(rows):.1%}); core={core_retrieved}/{len(core_rows)} ({core_retrieved / len(core_rows):.1%})")


if __name__ == "__main__":
    main()
