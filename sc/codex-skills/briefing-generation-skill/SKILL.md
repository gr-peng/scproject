---
name: briefing-generation-skill
description: Assemble search, ranking, summarization, visualization, and evaluation outputs into an illustrated Markdown report plus aligned CSV and JSON artifacts for a Daily arXiv Research Briefing pipeline. Use when Codex needs the final briefing-generation skill definition for an arXiv search, literature monitoring, paper triage, or briefing agent, especially when charts should be embedded directly in the report.
author: daily-arxiv-research-briefing-agent-team
version: 1.0.0
tags:
  - arxiv
  - briefing
  - report-generation
  - markdown
  - literature-mining
---

# Briefing Generation Skill

Define the final assembly contract for the fifth stage of the Daily arXiv Research Briefing Agent.

## Inputs

- structured paper metadata from `arxiv-search-skill`
- ranking scores and ranks from `paper-ranking-skill`
- summaries from `paper-summarization-skill`
- figure manifest, captions, alt text, and computed metrics from `visualization-skill`
- optional `top_k`, `run_id`, `query_id`, and output directory settings
- optional `previous_run_json` for report diffs across daily runs

## Output Contract

Write three aligned artifacts to the same directory:

- `daily-arxiv-briefing-YYYY-MM-DD.md`
- `daily-arxiv-briefing-YYYY-MM-DD.csv`
- `daily-arxiv-briefing-YYYY-MM-DD.json`
- `briefing-manifest-YYYY-MM-DD.json`
- optional `daily-arxiv-briefing-YYYY-MM-DD.docx` when a Word handout is requested

Treat JSON as the source of truth so Markdown and CSV can be regenerated from the same snapshot.

## Markdown Structure

Include these sections:

1. `Executive Summary`
2. `Evaluation Metrics`
3. `Visual Overview`
4. `Summary Table`
5. `Highlighted Papers`
6. `Notes`

The summary table should expose rank, title, arXiv identifier, relevance, novelty, category, published date, one-line summary, and links.
When multi-signal ranking is available, also expose citation/proxy, recency, method signal, and final score.

## Figure Embedding

Embed figures directly in Markdown using relative paths:

```markdown
![Alt text](figures/example.png)
```

Place the most useful overview figures before the paper table. Include every generated figure in the report unless the figure manifest marks it as optional or failed. Use captions under images so the report remains readable in plain Markdown viewers.
PNG is the default figure format for broad compatibility with Markdown, Word, and PowerPoint. SVG can be retained as an optional source format but should not be the primary embedded artifact.

## Required Metrics Section

Include a compact metrics table with:

- retrieved papers
- top-k papers
- mean relevance
- max relevance
- relevance lift at k
- high-value rate at k
- mean novelty
- mean citation/proxy score
- mean recency score
- mean method signal score
- coverage at k
- category diversity
- category evenness
- median recency in days
- summary completion rate
- summary specificity score
- link completeness rate
- figure generation success rate
- overall quality score

## Workflow

1. Join upstream payloads on `arxiv_id` or another agreed stable key.
2. Preserve rows even when some downstream fields are missing.
3. Build a skimmable Markdown briefing with embedded figures, tables, links, and short paragraphs.
4. Export a fixed-column CSV for annotation and metrics.
5. Export JSON with complete paper objects, metrics, figure manifest, and any warnings or errors.
6. Export a manifest containing output paths, row counts, metric coverage, embedded figure count, and warnings.
7. When a previous run is available, compute added, removed, and repeated papers.
8. Record run boundaries, missing fields, ranking fallback policy, and output paths in `Notes`.

## Guardrails

- Do not invent summaries or scores that upstream skills did not produce.
- If an upstream skill partially fails, still emit all three files and document the gap.
- Prefer relative figure paths inside the output directory convention.
- Keep row counts aligned with the contracted `top_k`, or explain every gap in `Notes`.
- Do not show raw filesystem absolute paths inside Markdown reports; keep paths portable.
- Verify that every embedded figure path exists before finishing.
- Make clear whether citation values are real counts or proxy impact scores.
- Keep Markdown, CSV, JSON, manifest, and optional Word output aligned on row counts and top-k ordering.

## Evaluation Signals

- `file_generation_success_rate`
- `section_completeness`
- `table_completeness`
- `link_validity_rate`
- `embedded_figure_count`
- `embedded_figure_path_validity_rate`
- `metric_completeness_rate`
- `figure_path_validity_rate`
- `ranking_component_completeness_rate`
- `docx_generation_success_rate`

## Deliverables

- `briefing_generation_skill.py`
- `briefing-manifest-YYYY-MM-DD.json`
- Markdown, CSV, JSON, and embedded figure artifacts
