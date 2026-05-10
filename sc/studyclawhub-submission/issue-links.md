# StudyClawHub Submission Pack

This file contains the values needed for the StudyClawHub submit form.
Open the linked GitHub issue URLs after replacing `TODO_GITHUB_REPO_URL` and `TODO_GITHUB_USERNAME` with real values.

Source instructions:
- Quickstart: https://trust-app-ai-lab.github.io/StudyClawHub/quickstart.html
- Submit page: https://trust-app-ai-lab.github.io/StudyClawHub/

## Skills to Submit

### arxiv-search-skill

- Type: Skill
- Name: `arxiv-search-skill`
- Description: Retrieve arXiv papers for a Daily arXiv Research Briefing pipeline by converting user topics into arXiv API queries, applying category and date filters, removing duplicates, and returning structured Paper objects. Use when Codex needs the retrieval-stage skill definition for an arXiv search, literature monitoring, or briefing agent.
- Version: `1.0.0`
- Tags: `arxiv, search, retrieval, literature-mining, social-network-analysis`
- GitHub Repo URL: `TODO_GITHUB_REPO_URL`
- Path to Skill Folder: `codex-skills/arxiv-search-skill`
- Agent name: `daily-arxiv-research-briefing-agent`
- GitHub Username: `TODO_GITHUB_USERNAME`
- Issue link: https://github.com/Trust-App-AI-Lab/StudyClawHub/issues/new?title=Submit+Skill%3A+arxiv-search-skill&body=%23%23+StudyClawHub+Submission%0A%0A-+Type%3A+Skill%0A-+Name%3A+arxiv-search-skill%0A-+Description%3A+Retrieve+arXiv+papers+for+a+Daily+arXiv+Research+Briefing+pipeline+by+converting+user+topics+into+arXiv+API+queries%2C+applying+category+and+date+filters%2C+removing+duplicates%2C+and+returning+structured+Paper+objects.+Use+when+Codex+needs+the+retrieval-stage+skill+definition+for+an+arXiv+search%2C+literature+monitoring%2C+or+briefing+agent.%0A-+Version%3A+1.0.0%0A-+Tags%3A+arxiv%2C+search%2C+retrieval%2C+literature-mining%2C+social-network-analysis%0A-+GitHub+Repo+URL%3A+TODO_GITHUB_REPO_URL%0A-+Path+to+Skill+Folder%3A+codex-skills%2Farxiv-search-skill%0A-+Agent+name%3A+daily-arxiv-research-briefing-agent%0A-+GitHub+Username%3A+TODO_GITHUB_USERNAME%0A%0A%23%23+Notes%0A%0AThis+skill+is+one+component+of+a+five-skill+Daily+arXiv+Research+Briefing+Agent.%0AThe+academic-ppt-generator+skill+is+intentionally+excluded+from+this+submission+set.

### paper-ranking-skill

- Type: Skill
- Name: `paper-ranking-skill`
- Description: Rank retrieved arXiv papers for a Daily arXiv Research Briefing pipeline by computing query-aware relevance and heuristic novelty scores, assigning ranks, and exporting ranked Paper objects. Use when Codex needs the ranking-stage skill definition for an arXiv search, literature monitoring, or briefing agent.
- Version: `1.0.0`
- Tags: `arxiv, ranking, relevance, citation-analysis, literature-mining`
- GitHub Repo URL: `TODO_GITHUB_REPO_URL`
- Path to Skill Folder: `codex-skills/paper-ranking-skill`
- Agent name: `daily-arxiv-research-briefing-agent`
- GitHub Username: `TODO_GITHUB_USERNAME`
- Issue link: https://github.com/Trust-App-AI-Lab/StudyClawHub/issues/new?title=Submit+Skill%3A+paper-ranking-skill&body=%23%23+StudyClawHub+Submission%0A%0A-+Type%3A+Skill%0A-+Name%3A+paper-ranking-skill%0A-+Description%3A+Rank+retrieved+arXiv+papers+for+a+Daily+arXiv+Research+Briefing+pipeline+by+computing+query-aware+relevance+and+heuristic+novelty+scores%2C+assigning+ranks%2C+and+exporting+ranked+Paper+objects.+Use+when+Codex+needs+the+ranking-stage+skill+definition+for+an+arXiv+search%2C+literature+monitoring%2C+or+briefing+agent.%0A-+Version%3A+1.0.0%0A-+Tags%3A+arxiv%2C+ranking%2C+relevance%2C+citation-analysis%2C+literature-mining%0A-+GitHub+Repo+URL%3A+TODO_GITHUB_REPO_URL%0A-+Path+to+Skill+Folder%3A+codex-skills%2Fpaper-ranking-skill%0A-+Agent+name%3A+daily-arxiv-research-briefing-agent%0A-+GitHub+Username%3A+TODO_GITHUB_USERNAME%0A%0A%23%23+Notes%0A%0AThis+skill+is+one+component+of+a+five-skill+Daily+arXiv+Research+Briefing+Agent.%0AThe+academic-ppt-generator+skill+is+intentionally+excluded+from+this+submission+set.

### paper-summarization-skill

- Type: Skill
- Name: `paper-summarization-skill`
- Description: Extract contribution, method, and concise brief summaries from ranked arXiv paper abstracts for a Daily arXiv Research Briefing pipeline. Use when Codex needs the summarization-stage skill definition for an arXiv search, literature monitoring, or briefing agent.
- Version: `1.0.0`
- Tags: `arxiv, summarization, paper-analysis, evidence-extraction, literature-mining`
- GitHub Repo URL: `TODO_GITHUB_REPO_URL`
- Path to Skill Folder: `codex-skills/paper-summarization-skill`
- Agent name: `daily-arxiv-research-briefing-agent`
- GitHub Username: `TODO_GITHUB_USERNAME`
- Issue link: https://github.com/Trust-App-AI-Lab/StudyClawHub/issues/new?title=Submit+Skill%3A+paper-summarization-skill&body=%23%23+StudyClawHub+Submission%0A%0A-+Type%3A+Skill%0A-+Name%3A+paper-summarization-skill%0A-+Description%3A+Extract+contribution%2C+method%2C+and+concise+brief+summaries+from+ranked+arXiv+paper+abstracts+for+a+Daily+arXiv+Research+Briefing+pipeline.+Use+when+Codex+needs+the+summarization-stage+skill+definition+for+an+arXiv+search%2C+literature+monitoring%2C+or+briefing+agent.%0A-+Version%3A+1.0.0%0A-+Tags%3A+arxiv%2C+summarization%2C+paper-analysis%2C+evidence-extraction%2C+literature-mining%0A-+GitHub+Repo+URL%3A+TODO_GITHUB_REPO_URL%0A-+Path+to+Skill+Folder%3A+codex-skills%2Fpaper-summarization-skill%0A-+Agent+name%3A+daily-arxiv-research-briefing-agent%0A-+GitHub+Username%3A+TODO_GITHUB_USERNAME%0A%0A%23%23+Notes%0A%0AThis+skill+is+one+component+of+a+five-skill+Daily+arXiv+Research+Briefing+Agent.%0AThe+academic-ppt-generator+skill+is+intentionally+excluded+from+this+submission+set.

### visualization-skill

- Type: Skill
- Name: `visualization-skill`
- Description: Generate publication-quality workflow diagrams, evaluation charts, and embeddable figure manifests for a Daily arXiv Research Briefing pipeline, including retrieval quality, ranking score diagnostics, topical/category coverage, recency, summarization coverage, and runtime views. Use when Codex needs the visualization-stage skill definition for an arXiv search, literature monitoring, paper triage, or briefing agent.
- Version: `1.0.0`
- Tags: `arxiv, visualization, evaluation, png-charts, literature-mining`
- GitHub Repo URL: `TODO_GITHUB_REPO_URL`
- Path to Skill Folder: `codex-skills/visualization-skill`
- Agent name: `daily-arxiv-research-briefing-agent`
- GitHub Username: `TODO_GITHUB_USERNAME`
- Issue link: https://github.com/Trust-App-AI-Lab/StudyClawHub/issues/new?title=Submit+Skill%3A+visualization-skill&body=%23%23+StudyClawHub+Submission%0A%0A-+Type%3A+Skill%0A-+Name%3A+visualization-skill%0A-+Description%3A+Generate+publication-quality+workflow+diagrams%2C+evaluation+charts%2C+and+embeddable+figure+manifests+for+a+Daily+arXiv+Research+Briefing+pipeline%2C+including+retrieval+quality%2C+ranking+score+diagnostics%2C+topical%2Fcategory+coverage%2C+recency%2C+summarization+coverage%2C+and+runtime+views.+Use+when+Codex+needs+the+visualization-stage+skill+definition+for+an+arXiv+search%2C+literature+monitoring%2C+paper+triage%2C+or+briefing+agent.%0A-+Version%3A+1.0.0%0A-+Tags%3A+arxiv%2C+visualization%2C+evaluation%2C+png-charts%2C+literature-mining%0A-+GitHub+Repo+URL%3A+TODO_GITHUB_REPO_URL%0A-+Path+to+Skill+Folder%3A+codex-skills%2Fvisualization-skill%0A-+Agent+name%3A+daily-arxiv-research-briefing-agent%0A-+GitHub+Username%3A+TODO_GITHUB_USERNAME%0A%0A%23%23+Notes%0A%0AThis+skill+is+one+component+of+a+five-skill+Daily+arXiv+Research+Briefing+Agent.%0AThe+academic-ppt-generator+skill+is+intentionally+excluded+from+this+submission+set.

### briefing-generation-skill

- Type: Skill
- Name: `briefing-generation-skill`
- Description: Assemble search, ranking, summarization, visualization, and evaluation outputs into an illustrated Markdown report plus aligned CSV and JSON artifacts for a Daily arXiv Research Briefing pipeline. Use when Codex needs the final briefing-generation skill definition for an arXiv search, literature monitoring, paper triage, or briefing agent, especially when charts should be embedded directly in the report.
- Version: `1.0.0`
- Tags: `arxiv, briefing, report-generation, markdown, literature-mining`
- GitHub Repo URL: `TODO_GITHUB_REPO_URL`
- Path to Skill Folder: `codex-skills/briefing-generation-skill`
- Agent name: `daily-arxiv-research-briefing-agent`
- GitHub Username: `TODO_GITHUB_USERNAME`
- Issue link: https://github.com/Trust-App-AI-Lab/StudyClawHub/issues/new?title=Submit+Skill%3A+briefing-generation-skill&body=%23%23+StudyClawHub+Submission%0A%0A-+Type%3A+Skill%0A-+Name%3A+briefing-generation-skill%0A-+Description%3A+Assemble+search%2C+ranking%2C+summarization%2C+visualization%2C+and+evaluation+outputs+into+an+illustrated+Markdown+report+plus+aligned+CSV+and+JSON+artifacts+for+a+Daily+arXiv+Research+Briefing+pipeline.+Use+when+Codex+needs+the+final+briefing-generation+skill+definition+for+an+arXiv+search%2C+literature+monitoring%2C+paper+triage%2C+or+briefing+agent%2C+especially+when+charts+should+be+embedded+directly+in+the+report.%0A-+Version%3A+1.0.0%0A-+Tags%3A+arxiv%2C+briefing%2C+report-generation%2C+markdown%2C+literature-mining%0A-+GitHub+Repo+URL%3A+TODO_GITHUB_REPO_URL%0A-+Path+to+Skill+Folder%3A+codex-skills%2Fbriefing-generation-skill%0A-+Agent+name%3A+daily-arxiv-research-briefing-agent%0A-+GitHub+Username%3A+TODO_GITHUB_USERNAME%0A%0A%23%23+Notes%0A%0AThis+skill+is+one+component+of+a+five-skill+Daily+arXiv+Research+Briefing+Agent.%0AThe+academic-ppt-generator+skill+is+intentionally+excluded+from+this+submission+set.
