# Aborted uncheckpointed search run

This run was stopped on 10 September 2026 after approximately 20 minutes.
The previous implementation retained retrieved records only in memory and had
not completed any durable result or query-log checkpoint. No candidate counts
from this directory are used in the review. The run motivated per-source-query
raw JSONL and query-log checkpointing in the next public-v2 run.
