# Daily arXiv Research Briefing Agent

This repository contains a five-skill Agent for the StudyClawHub final project topic **Daily arXiv Research Briefing Agent**.

Given a research topic or keywords, the Agent retrieves recent arXiv papers, ranks them with multi-signal scoring, extracts contribution and method summaries, generates PNG evaluation figures, and assembles a structured briefing report.

## Submitted Skills

1. `arxiv-search-skill`: retrieves arXiv papers and returns structured paper metadata.
2. `paper-ranking-skill`: ranks papers with relevance, novelty, citation/proxy, recency, and method signals.
3. `paper-summarization-skill`: extracts contribution, method, evidence, and brief summaries.
4. `visualization-skill`: computes evaluation metrics and generates PNG figures.
5. `briefing-generation-skill`: assembles Markdown, CSV, JSON, manifest, and report artifacts.

The `academic-ppt-generator` skill is intentionally excluded from StudyClawHub submission.

## Repository Layout

```text
codex-skills/
  arxiv-search-skill/SKILL.md
  paper-ranking-skill/SKILL.md
  paper-summarization-skill/SKILL.md
  visualization-skill/SKILL.md
  briefing-generation-skill/SKILL.md
```

## Evaluation

The visualization skill evaluates retrieval health, ranking utility, freshness, category diversity, summary usefulness, link/source integrity, figure generation success, and runtime efficiency.

## Citation Note

arXiv metadata does not directly provide citation counts. The ranking skill supports real `citation_count` values when an external source such as Semantic Scholar or OpenAlex is available. When citation data is unavailable, the system uses a clearly labeled `impact_proxy_score` rather than inventing citations.
