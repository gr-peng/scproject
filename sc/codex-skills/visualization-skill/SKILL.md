---
name: visualization-skill
description: Generate publication-quality workflow diagrams, evaluation charts, and embeddable figure manifests for a Daily arXiv Research Briefing pipeline, including retrieval quality, ranking score diagnostics, topical/category coverage, recency, summarization coverage, and runtime views. Use when Codex needs the visualization-stage skill definition for an arXiv search, literature monitoring, paper triage, or briefing agent.
author: daily-arxiv-research-briefing-agent-team
version: 1.0.0
tags:
  - arxiv
  - visualization
  - evaluation
  - png-charts
  - literature-mining
---

# Visualization Skill

Define the visualization contract for the fourth stage of the Daily arXiv Research Briefing Agent.

## Inputs

- `papers: list[Paper]` after ranking and optional summarization
- evaluation metrics computed from structured search, ranking, summary, and generation outputs
- optional baseline score tables such as `latest-first`, `tfidf`, and `tfidf_novelty`
- `top_k`, `query_id`, and output directory metadata as needed

## Output Contract

Return a figure manifest that can be embedded directly by `briefing-generation-skill`:

- `figure_id`
- `path`
- `caption`
- `alt_text`
- `kind`
- `width`
- optional `query_id`
- optional `paper_id` or `arxiv_id`

Persist figure files under `outputs/figures/` or another documented directory. Prefer SVG for Markdown portability and sharp rendering; use PNG only when the plotting stack requires raster output.
Persist primary figure files as PNG so the briefing can be embedded consistently in Markdown, Word, and PowerPoint. SVG may be kept only as an optional editable source artifact.

## Required Metrics

Compute metrics from the pipeline artifacts without requiring human labels. Group them by what a
Daily arXiv Research Briefing Agent must prove:

### Retrieval Health

1. `retrieved_count`: number of deduplicated papers returned by search.
2. `retrieval_yield_rate`: `retrieved_count / requested_max_results` when the request cap is known.
3. `metadata_completeness_rate`: share of retrieved papers with title, abstract, date, category, and links.
4. `source_integrity_rate`: share of retrieved papers with a parseable arXiv id, abstract URL, PDF URL, and publication date.

### Ranking Utility

5. `mean_relevance_score`, `median_relevance_score`, and `max_relevance_score`.
6. `relevance_lift_at_k`: top-k mean relevance divided by full-corpus mean relevance.
7. `coverage_at_k`: share of top-k papers whose relevance score is greater than zero.
8. `high_value_rate_at_k`: share of top-k papers with above-corpus-median relevance and non-trivial novelty.
9. `score_spread_at_k`: standard deviation of final scores in top-k; low spread warns that ranking may not separate papers.
10. `mean_citation_score`: normalized citation count when available, otherwise explicit citation-neutral proxy score.
11. `mean_recency_score`: average recency score in the selected top-k papers.
12. `mean_method_signal_score`: average method/evaluation cue strength in the selected papers.

### Freshness and Diversity

13. `freshness_at_k`: share of top-k papers published within 7 days of the run date.
14. `recency_days_median`: median paper age in days.
15. `category_diversity`: number of unique primary categories in top-k papers.
16. `category_evenness`: normalized entropy of top-k primary-category distribution.

### Summary Usefulness

17. `summary_completion_rate`: share of top-k papers with contribution, method, and brief summaries.
18. `summary_specificity_score`: average normalized length and field coverage of generated summaries.
19. `brief_actionability_rate`: share of top-k papers whose brief summary is long enough to support skimming.

### Report Reliability and Efficiency

20. `link_completeness_rate`: share of top-k papers with both abstract and PDF links.
21. `figure_generation_success_rate`: generated required figures divided by attempted required figures.
22. `runtime_seconds` and `runtime_per_paper_seconds`.
23. `overall_quality_score`: weighted roll-up of retrieval, ranking, freshness, diversity, summary, integrity, figure, and efficiency signals.

## Required Figures

Generate at least these chart families:

1. `evaluation_scorecard.png`: a compact dashboard with overall quality score and grouped scores for retrieval, ranking, freshness, diversity, summary, integrity, visualization, and runtime.
2. `quality_radar.png`: an 8-axis radar chart showing the same grouped scores for quick weakness detection.
3. `top_paper_matrix.png`: a ranked matrix showing relevance, novelty, citation/proxy, recency, method signal, final score, and summary readiness for top-k papers.
4. `category_distribution.png`: category distribution bar chart with category share and count labels.
5. `relevance_recency.png`: relevance-vs-recency scatter plot, with point size/color reflecting final score.
6. `score_distribution.png`: score distribution chart for relevance, novelty, citation/proxy, method signal, and final score.
7. `summary_quality.png`: completion, specificity, and actionability indicators for summary outputs.
8. `runtime_by_stage.png`: runtime-by-stage chart when timing logs exist.
9. Optional `baseline_comparison.png`: compare `latest-first`, `tfidf`, `tfidf_novelty`, and `multi_signal` when baseline data or human labels exist.

## Workflow

1. Read structured experiment outputs rather than scraping values from screenshots.
2. Compute the required metrics before plotting and include them in the returned manifest.
3. Validate that each requested figure has enough data to render.
4. Generate PNG charts with clear titles, labeled axes, consistent colors, and stable filenames.
5. Return figure paths, captions, and alt text for downstream Markdown embedding.
6. Record missing-data warnings when a requested chart cannot be rendered.

## Guardrails

- Keep charts consistent with CSV and JSON metrics; never hand-edit chart values.
- Prefer reproducible code-generated figures over manual screenshots.
- Treat figure generation as non-blocking: if one chart fails, generate the rest and report the failure.
- Store relative paths when possible so `briefing-generation-skill` can embed figures cleanly.
- Avoid chart junk: use restrained palettes, readable axis labels, adequate margins, and values sorted in the order that helps comparison.
- Do not plot metrics that require human labels unless those labels are explicitly present.

## Evaluation Signals

- `figure_generation_success_rate`
- `required_metric_coverage`
- `embedded_figure_count`
- `chart_data_consistency`
- `number_of_valid_figures`
- `missing_data_warning_count`
- `overall_quality_score`
- `metric_group_coverage`
- `visual_readability_review`

## Deliverables

- `visualization_skill.py`
- chart outputs such as `evaluation_scorecard.png`, `quality_radar.png`, `top_paper_matrix.png`, `category_distribution.png`, `relevance_recency.png`, `score_distribution.png`, `summary_quality.png`, `runtime_by_stage.png`
- optional Mermaid source for the workflow diagram
