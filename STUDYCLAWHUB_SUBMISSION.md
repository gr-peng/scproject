# StudyClawHub Submission Checklist

Repository: https://github.com/gr-peng/scproject
Agent: `daily-arxiv-research-briefing-agent`
GitHub username: `gr-peng`

The academic-ppt-generator skill is intentionally excluded.

## Skills

### arxiv-search-skill

- Type: Skill
- Name: `arxiv-search-skill`
- Description: Retrieve arXiv papers for a Daily arXiv Research Briefing pipeline by converting user topics into arXiv API queries, applying category and date filters, removing duplicates, and returning structured Paper objects.
- Version: `1.0.0`
- Tags: `arxiv, search, retrieval, literature-mining, social-network-analysis`
- GitHub Repo URL: `https://github.com/gr-peng/scproject`
- Path to Skill Folder: `codex-skills/arxiv-search-skill`

### paper-ranking-skill

- Type: Skill
- Name: `paper-ranking-skill`
- Description: Rank retrieved arXiv papers with relevance, novelty, citation/proxy, recency, method-signal, and final-score dimensions.
- Version: `1.0.0`
- Tags: `arxiv, ranking, relevance, citation-analysis, literature-mining`
- GitHub Repo URL: `https://github.com/gr-peng/scproject`
- Path to Skill Folder: `codex-skills/paper-ranking-skill`

### paper-summarization-skill

- Type: Skill
- Name: `paper-summarization-skill`
- Description: Extract contribution, method, evidence sentences, quality flags, and concise brief summaries from ranked arXiv paper abstracts.
- Version: `1.0.0`
- Tags: `arxiv, summarization, paper-analysis, evidence-extraction, literature-mining`
- GitHub Repo URL: `https://github.com/gr-peng/scproject`
- Path to Skill Folder: `codex-skills/paper-summarization-skill`

### visualization-skill

- Type: Skill
- Name: `visualization-skill`
- Description: Generate PNG evaluation figures and metric manifests for a Daily arXiv Research Briefing pipeline.
- Version: `1.0.0`
- Tags: `arxiv, visualization, evaluation, png-charts, literature-mining`
- GitHub Repo URL: `https://github.com/gr-peng/scproject`
- Path to Skill Folder: `codex-skills/visualization-skill`

### briefing-generation-skill

- Type: Skill
- Name: `briefing-generation-skill`
- Description: Assemble search, ranking, summarization, visualization, and evaluation outputs into aligned Markdown, CSV, JSON, manifest, and optional Word artifacts.
- Version: `1.0.0`
- Tags: `arxiv, briefing, report-generation, markdown, literature-mining`
- GitHub Repo URL: `https://github.com/gr-peng/scproject`
- Path to Skill Folder: `codex-skills/briefing-generation-skill`
