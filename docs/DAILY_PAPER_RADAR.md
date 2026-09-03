# Daily Paper Radar

The radar runs each day at 02:17 UTC and can be started manually in GitHub Actions. It searches six modality and capability-specific query families on arXiv, OpenAlex, and Crossref.

Each run produces a deduplicated candidate inbox, a readable daily digest, and a query audit containing per-source counts and failures. The workflow opens or updates a reviewable pull request; it never promotes candidates into the reviewed literature list automatically.

Scheduled Actions are best-effort: the audit file distinguishes a quiet day from a delayed or failed source.
