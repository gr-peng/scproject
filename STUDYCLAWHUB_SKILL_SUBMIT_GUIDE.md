# StudyClawHub Skill Submission Guide

This repository contains one agent and five StudyClawHub skills for the Daily arXiv Research Briefing project.

## Important Rule

StudyClawHub validates the path differently depending on the selected type:

- Type `agent`: the path must contain `AGENTS.md` or `CLAUDE.md`.
- Type `skill`: the path must contain `SKILL.md` directly.

Therefore, submitting only `codex-skills` as an agent registers the agent, but it does not automatically register the five skills. Each skill must be submitted separately.

## Agent Submission

Use this only for the orchestration agent.

| Field | Value |
| --- | --- |
| Type | `agent` |
| Name | `arxiv-deep-briefing-agent` |
| Repo | `https://github.com/gr-peng/scproject` |
| Path | `codex-skills` |
| GitHub Username | `gr-peng` |

## Skill Submissions

Submit the following five entries one by one with Type `skill`.

| Type | Name | Path | Description |
| --- | --- | --- | --- |
| `skill` | `arxiv-search-skill` | `codex-skills/arxiv-search-skill` | Retrieve recent arXiv papers, deduplicate results, filter by category/date, and return structured paper metadata. |
| `skill` | `paper-ranking-skill` | `codex-skills/paper-ranking-skill` | Rank papers using relevance, novelty, citation/proxy, recency, method signal, and final score dimensions. |
| `skill` | `paper-summarization-skill` | `codex-skills/paper-summarization-skill` | Generate contribution summaries, method summaries, evidence sentences, brief summaries, and quality flags. |
| `skill` | `visualization-skill` | `codex-skills/visualization-skill` | Generate PNG evaluation figures for retrieval quality, ranking diagnostics, coverage, freshness, summary quality, and runtime. |
| `skill` | `briefing-generation-skill` | `codex-skills/briefing-generation-skill` | Assemble search, ranking, summarization, and visualization outputs into Markdown, CSV, JSON, manifest, and optional Word reports. |

## Common Fields

Use these shared values for every skill submission:

| Field | Value |
| --- | --- |
| Version | `0.1.0` |
| GitHub Repo URL | `https://github.com/gr-peng/scproject` |
| GitHub Username | `gr-peng` |
| Agent name | `arxiv-deep-briefing-agent` |

## Do Not Submit

Do not submit `academic-ppt-generator`; it is excluded from the project skill submission.

Do not use paths under `sc/codex-skills/...` for StudyClawHub. The official submission paths are the root-level `codex-skills/...` paths listed above.
