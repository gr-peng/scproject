---
name: paper-summarization-skill
description: Extract contribution, method, and concise brief summaries from ranked arXiv paper abstracts for a Daily arXiv Research Briefing pipeline. Use when Codex needs the summarization-stage skill definition for an arXiv search, literature monitoring, or briefing agent.
author: gr-peng
version: 1.0.0
tags:
  - arxiv
  - summarization
  - paper-analysis
  - evidence-extraction
  - literature-mining
---

# Paper Summarization Skill

Define the summarization contract for the third stage of the Daily arXiv Research Briefing Agent.

## Inputs

- `papers: list[Paper]` after retrieval and ranking

Each paper should include at least:

- `paper_id`
- `title`
- `summary`
- `published`
- `url`
- `pdf_url`
- `categories`
- `primary_category`
- ranking signals such as `relevance_score`, `novelty_score`, `method_signal_score`, and `score_breakdown` when available

## Output Contract

Return `list[Paper]` and populate:

- `contribution_summary`
- `method_summary`
- `brief_summary`
- `evidence_sentences`
- `summary_quality_flags`
- `fallback_used`

Track whether fallback extraction was used so evaluation can compute `fallback_rate`.

## Workflow

1. Split each abstract into sentences with simple punctuation rules.
2. Extract contribution sentences by prioritizing cues such as `propose`, `present`, `introduce`, `develop`, `we show`, and `we demonstrate`.
3. Extract method sentences by prioritizing cues such as `method`, `approach`, `framework`, `model`, `algorithm`, `architecture`, `training`, `evaluation`, and `benchmark`.
4. Extract evidence sentences that support the ranking signals, especially novelty and method strength.
5. Build a 2-3 sentence `brief_summary` from `primary_category`, contribution, method, and ranking reason.
6. Attach `summary_quality_flags` such as `has_contribution`, `has_method`, `has_evidence`, `brief_is_actionable`, and `fallback_used`.
7. If no rule-based extraction succeeds, fall back to the first two abstract sentences and mark the sample as fallback-based.

## Guardrails

- Do not re-run retrieval or ranking logic here.
- Do not fabricate technical claims that are absent from the abstract.
- Keep output paper-centric and independent from final briefing formatting.
- On extraction failure, degrade gracefully instead of failing the whole agent.
- Keep extracted evidence sentence indices so later review can trace every generated sentence back to the abstract.
- Do not use ranking scores to claim paper quality; use them only to explain why the agent selected the paper.

## Evaluation Signals

- `contribution_correctness`
- `method_correctness`
- `readability`
- `extraction_success_rate`
- `fallback_rate`
- `summary_length`
- `evidence_coverage_rate`
- `brief_actionability_rate`
- `summary_specificity_score`

Use human 1-5 scoring for correctness and readability.

## Deliverables

- `paper_summarization_skill.py`
- `summary_scores.csv` or `summary_scores_template.csv`
- exported paper-level summary annotations for evaluation
