---
name: arxiv-search-skill
description: Retrieve arXiv papers for a Daily arXiv Research Briefing pipeline by converting user topics into arXiv API queries, applying category and date filters, removing duplicates, and returning structured Paper objects. Use when Codex needs the retrieval-stage skill definition for an arXiv search, literature monitoring, or briefing agent.
author: daily-arxiv-research-briefing-agent-team
version: 1.0.0
tags:
  - arxiv
  - search
  - retrieval
  - literature-mining
  - social-network-analysis
---

# Arxiv Search Skill

Define the retrieval contract for the first stage of the Daily arXiv Research Briefing Agent.

## Inputs

- `keywords: list[str]` as the required research topics.
- `categories: list[str] | None` for optional arXiv category filters such as `cs.LG` or `cs.AI`.
- `max_results: int` for the retrieval cap.
- `days_back: int | None` or `start_date/end_date` for local date filtering.
- `sort_by` and `sort_order` for API ordering.
- `query_expansion: bool` to expand topic terms with controlled synonyms and category hints.
- `enrich_citations: bool` for optional downstream citation enrichment from sources such as Semantic Scholar or OpenAlex when available.
- `save_results: bool` for optional CSV and JSON export.

## Output Contract

Return `list[Paper]` where each paper includes:

- `paper_id`, `title`, `authors`, `summary`
- `published`, `updated`
- `url`, `pdf_url`
- `categories`, `primary_category`
- `metadata_complete`, `source_integrity`, and `query_match_terms`
- optional enrichment fields: `citation_count`, `citation_source`, `citation_checked_at`
- reserved downstream fields: `relevance_score`, `novelty_score`, `citation_score`, `recency_score`, `method_signal_score`, `final_score`, `contribution_summary`, `method_summary`, `brief_summary`

Save artifacts under `outputs/search/` when persistence is enabled.

## Workflow

1. Parse user keywords, normalize category filters, and create a transparent query plan.
2. Expand query terms only from a documented synonym map, e.g. `agentic -> ai agent, autonomous agent, multi-agent`.
3. Build a valid arXiv query such as `(all:"graph neural networks" OR all:"social network analysis") AND (cat:cs.LG OR cat:cs.SI)`.
4. Call `https://export.arxiv.org/api/query` with a controlled `max_results`.
5. Parse XML metadata into `Paper` objects.
6. Remove duplicate `paper_id` entries and record duplicate count.
7. Apply local date filtering after retrieval when a date window is provided.
8. Mark metadata completeness and source integrity for later visualization.
9. Optionally enrich citation counts from an external scholarly API; if enrichment is unavailable, leave `citation_count=None` and let ranking use an explicit proxy score.
10. Return the final paper list and optionally write CSV and JSON outputs.

## Guardrails

- Keep retrieval independent from ranking, summarization, visualization, and briefing generation.
- Treat API failures as recoverable: return an empty list plus error metadata instead of crashing the pipeline.
- Do not invent missing metadata. Leave fields empty or `None` when unavailable.
- Do not invent citation counts. If no citation API result is available, store `citation_count=None`.
- Use retry and backoff for HTTP 429 or transient network failures.
- Keep every generated query string and expansion term in the output so retrieval is auditable.

## Downstream Dependencies

- `paper-ranking-skill` consumes `title`, `summary`, `categories`, and `primary_category`.
- `paper-summarization-skill` consumes `title` and `summary`.
- `visualization-skill` consumes category, date, and later ranking scores.
- `briefing-generation-skill` consumes the complete paper objects plus downstream annotations.

## Evaluation Signals

- `retrieved_count`
- `valid_metadata_rate`
- `duplicate_rate`
- `category_coverage`
- `query_expansion_count`
- `source_integrity_rate`
- `citation_enrichment_rate`
- `empty_result_rate`
- `runtime_seconds`

## Deliverables

- `skills/arxiv_search_skill.py`
- `utils/data_models.py`
- `run_search.py`
- `test_arxiv_search_skill.py`
- `evaluate_search_skill.py`
- `visualize_search_results.py`
