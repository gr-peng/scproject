# Daily arXiv Research Briefing Agent

This agent orchestrates five StudyClawHub skills to produce a personalized daily arXiv research briefing.

## Agent Goal

Given a research topic or a set of keywords, the agent retrieves recent arXiv papers, ranks them by research value, extracts contribution and method summaries, generates evaluation figures, and assembles a structured briefing report.

## Component Skills

1. `arxiv-search-skill`
   - Path: `codex-skills/arxiv-search-skill`
   - Role: Convert user topics into arXiv API queries, retrieve paper metadata, deduplicate results, apply date/category filters, and return structured Paper objects.

2. `paper-ranking-skill`
   - Path: `codex-skills/paper-ranking-skill`
   - Role: Rank retrieved papers with relevance, novelty, citation/proxy, recency, method signal, and final score dimensions.

3. `paper-summarization-skill`
   - Path: `codex-skills/paper-summarization-skill`
   - Role: Extract contribution summaries, method summaries, evidence sentences, brief summaries, and quality flags from paper abstracts.

4. `visualization-skill`
   - Path: `codex-skills/visualization-skill`
   - Role: Compute evaluation metrics and generate PNG figures such as scorecards, radar charts, top-paper matrices, category distributions, relevance-recency plots, score distributions, summary-quality charts, and runtime charts.

5. `briefing-generation-skill`
   - Path: `codex-skills/briefing-generation-skill`
   - Role: Assemble search, ranking, summarization, and visualization outputs into aligned Markdown, CSV, JSON, manifest, and optional Word artifacts.

## Workflow

1. Receive a user research topic or keyword set.
2. Invoke `arxiv-search-skill` to retrieve structured recent papers.
3. Invoke `paper-ranking-skill` to score and sort papers into a top-k shortlist.
4. Invoke `paper-summarization-skill` to extract contribution and method summaries.
5. Invoke `visualization-skill` to compute quality metrics and generate PNG figures.
6. Invoke `briefing-generation-skill` to produce the final briefing report.

## Evaluation

The agent is evaluated with retrieval health, ranking utility, freshness, category diversity, summary usefulness, link/source integrity, figure generation success, and runtime efficiency.

## Notes

The `academic-ppt-generator` folder is not part of this StudyClawHub submission. The official agent path for StudyClawHub is `codex-skills`, because this directory now contains this `AGENTS.md` file and the five component skill folders.
