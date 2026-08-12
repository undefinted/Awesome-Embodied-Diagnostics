.PHONY: all test clean

all:
	python3 scripts/build_bibtex.py
	python3 scripts/build_inventory.py
	python3 scripts/extract_citations.py
	python3 scripts/validate_bibliography.py
	python3 scripts/count_words.py
	python3 scripts/build_manifest.py

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -f results/citation_usage.csv results/missing_citations.csv results/section_word_counts.csv results/run_manifest.json literature/references.bib

