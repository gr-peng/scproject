---
name: paper-ranking-skill
description: Rank retrieved arXiv papers for a Daily arXiv Research Briefing pipeline by computing query-aware relevance and heuristic novelty scores, assigning ranks, and exporting ranked Paper objects. Use when Codex needs the ranking-stage skill definition for an arXiv search, literature monitoring, or briefing agent.
author: daily-arxiv-research-briefing-agent-team
version: 1.0.0
tags:
  - arxiv
  - ranking
  - relevance
  - citation-analysis
  - literature-mining
---

# Paper Ranking Skill

Define the ranking contract for the second stage of the Daily arXiv Research Briefing Agent.

## Inputs

- `papers: list[Paper]` from `arxiv-search-skill`
- `user_interests: list[str]`

Each `Paper` should already contain core metadata and abstract text.

## Output Contract

Return `list[Paper]` sorted by final score and populate:

- `relevance_score`
- `novelty_score`
- `citation_score`
- `recency_score`
- `method_signal_score`
- `impact_proxy_score`
- `rank`
- `score_breakdown`

Optionally export ranked CSV and JSON files under `outputs/ranking/`.

## Workflow

1. Build `paper_text` from `title + summary + categories`.
2. Build `query_text` from `user_interests`.
3. Compute query-aware `relevance_score` with deterministic lexical overlap or TF-IDF/BM25 when available.
4. Compute `novelty_score` from contribution cues such as `novel`, `new`, `benchmark`, `dataset`, `framework`, `first`, and `efficient`.
5. Compute `citation_score` from normalized real citation counts when `citation_count` exists. Do not fabricate citations.
6. When real citations are unavailable, compute `impact_proxy_score` from citation-neutral signals: author count, abstract specificity, category breadth, and title/method cues. Keep this field separate from `citation_count`.
7. Compute `recency_score` from publication age so daily briefings favor fresh papers without ignoring older high-value papers.
8. Compute `method_signal_score` from technical method cues such as `framework`, `algorithm`, `architecture`, `training`, `evaluation`, `benchmark`, and `dataset`.
9. Fuse scores with a documented default formula:
   `0.45 relevance + 0.20 novelty + 0.15 citation_or_proxy + 0.10 recency + 0.10 method_signal`.
10. Store `score_breakdown` with every component and weight.
11. Sort descending and assign one-based `rank`.

## Guardrails

- Do not alter retrieval logic or summarization fields here.
- Keep the scoring process deterministic enough to support ablation and report reproduction.
- Log empty or suspiciously short `paper_text` values because they weaken TF-IDF ranking.
- Preserve all papers even if a score is zero.
- Real citation counts must be labeled with `citation_source`; proxy scores must be labeled as proxy and never presented as real citations.
- If a component is unavailable, redistribute its weight only through a documented fallback policy.

## Required Ablation

Compare at least these strategies on the same queries:

- `latest-first`
- `tfidf`
- `tfidf_novelty`
- `tfidf_novelty_recency`
- `multi_signal` with relevance, novelty, citation/proxy, recency, and method signals

## Evaluation Signals

- `Precision@5`
- `Precision@10`
- `nDCG@10`
- `average_relevance_label`
- `mean_relevance_score`
- `mean_citation_score`
- `mean_recency_score`
- `mean_method_signal_score`
- `ranking_score_spread`
- `ablation_improvement`

Use human labels with `2 = highly relevant`, `1 = partially relevant`, `0 = irrelevant`.

## Deliverables

- `paper_ranking_skill.py`
- `ranking_ablation.py`
- `ranking_labels_template.csv`
