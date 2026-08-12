PYTHON ?= python3

.PHONY: all validate outputs workbook links crossref manifest package clean

all: validate outputs

validate:
	$(PYTHON) scripts/validate_catalog.py

outputs:
	$(PYTHON) scripts/build_outputs.py

workbook:
	$${CODEX_PRIMARY_RUNTIME_NODE:-node} scripts/build_workbook.mjs

links:
	$(PYTHON) scripts/check_links.py

crossref:
	$(PYTHON) scripts/query_crossref.py

manifest:
	$(PYTHON) scripts/build_manifest.py

package: all manifest
	$(PYTHON) scripts/package_release.py

clean:
	rm -f data/references.json data/references.bib results/coverage_by_section.csv results/coverage_summary.md results/validation_report.txt results/link_check.csv results/crossref_suggestions.json outputs/literature_catalog.xlsx outputs/literature_catalog_preview.png
