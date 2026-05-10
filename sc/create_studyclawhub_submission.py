import argparse
import json
import re
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT / "codex-skills"
OUT_DIR = ROOT / "studyclawhub-submission"
AGENT_NAME = "daily-arxiv-research-briefing-agent"

SKILL_DIRS = [
    "arxiv-search-skill",
    "paper-ranking-skill",
    "paper-summarization-skill",
    "visualization-skill",
    "briefing-generation-skill",
]


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    data = {}
    current_key = None
    for raw_line in match.group(1).splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')
            current_key = key
            if value:
                data[key] = value
            else:
                data[key] = []
    return data


def issue_url(record: dict) -> str:
    title = f"Submit Skill: {record['name']}"
    body = "\n".join(
        [
            "## StudyClawHub Submission",
            "",
            f"- Type: Skill",
            f"- Name: {record['name']}",
            f"- Description: {record['description']}",
            f"- Version: {record['version']}",
            f"- Tags: {', '.join(record['tags'])}",
            f"- GitHub Repo URL: {record['repo_url']}",
            f"- Path to Skill Folder: {record['path']}",
            f"- Agent name: {record['agent_name']}",
            f"- GitHub Username: {record['github_username']}",
            "",
            "## Notes",
            "",
            "This skill is one component of a five-skill Daily arXiv Research Briefing Agent.",
            "The academic-ppt-generator skill is intentionally excluded from this submission set.",
        ]
    )
    query = urllib.parse.urlencode({"title": title, "body": body})
    return f"https://github.com/Trust-App-AI-Lab/StudyClawHub/issues/new?{query}"


def build_records(repo_url: str, github_username: str) -> list:
    records = []
    for skill_dir in SKILL_DIRS:
        skill_path = SKILL_ROOT / skill_dir / "SKILL.md"
        meta = parse_frontmatter(skill_path)
        record = {
            "type": "Skill",
            "name": meta.get("name", skill_dir),
            "description": meta.get("description", ""),
            "version": meta.get("version", "1.0.0"),
            "tags": meta.get("tags", []),
            "repo_url": repo_url,
            "path": f"codex-skills/{skill_dir}",
            "agent_name": AGENT_NAME,
            "github_username": github_username,
        }
        record["issue_url"] = issue_url(record)
        records.append(record)
    return records


def write_markdown(records: list, path: Path) -> None:
    lines = [
        "# StudyClawHub Submission Pack",
        "",
        "This file contains the values needed for the StudyClawHub submit form.",
        "Open the linked GitHub issue URLs after replacing `TODO_GITHUB_REPO_URL` and `TODO_GITHUB_USERNAME` with real values.",
        "",
        "Source instructions:",
        "- Quickstart: https://trust-app-ai-lab.github.io/StudyClawHub/quickstart.html",
        "- Submit page: https://trust-app-ai-lab.github.io/StudyClawHub/",
        "",
        "## Skills to Submit",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"### {record['name']}",
                "",
                f"- Type: Skill",
                f"- Name: `{record['name']}`",
                f"- Description: {record['description']}",
                f"- Version: `{record['version']}`",
                f"- Tags: `{', '.join(record['tags'])}`",
                f"- GitHub Repo URL: `{record['repo_url']}`",
                f"- Path to Skill Folder: `{record['path']}`",
                f"- Agent name: `{record['agent_name']}`",
                f"- GitHub Username: `{record['github_username']}`",
                f"- Issue link: {record['issue_url']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate StudyClawHub submission metadata for the five non-PPT skills.")
    parser.add_argument("--repo-url", default="TODO_GITHUB_REPO_URL")
    parser.add_argument("--github-username", default="TODO_GITHUB_USERNAME")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = build_records(args.repo_url, args.github_username)
    (OUT_DIR / "submissions.json").write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(records, OUT_DIR / "issue-links.md")

    csv_lines = ["type,name,description,version,tags,repo_url,path,agent_name,github_username"]
    for record in records:
        row = [
            record["type"],
            record["name"],
            record["description"].replace(",", ";"),
            record["version"],
            "|".join(record["tags"]),
            record["repo_url"],
            record["path"],
            record["agent_name"],
            record["github_username"],
        ]
        csv_lines.append(",".join(row))
    (OUT_DIR / "submit-form-values.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
