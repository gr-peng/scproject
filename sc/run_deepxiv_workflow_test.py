import argparse
import csv
import html
import json
import math
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RUN_TZ = timezone(timedelta(hours=8))
RUN_DATE = datetime.now(RUN_TZ).date().isoformat()
PALETTE = {
    "ink": "#1f2933",
    "muted": "#64748b",
    "grid": "#d8dee9",
    "paper": "#ffffff",
    "panel": "#f7f9fc",
    "panel_alt": "#eef4f7",
    "navy": "#17324d",
    "teal": "#2f7d7e",
    "blue": "#3767a6",
    "green": "#4f8f5b",
    "gold": "#c58b2b",
    "rose": "#b85c70",
    "purple": "#6f5aa8",
    "cyan": "#3a8fb7",
    "orange": "#d47d35",
    "red": "#c25757",
}


@dataclass
class Paper:
    paper_id: str
    title: str
    authors: List[str]
    summary: str
    published: str
    updated: str
    url: str
    pdf_url: str
    categories: List[str]
    primary_category: str
    citation_count: Optional[int] = None
    citation_source: Optional[str] = None
    relevance_score: Optional[float] = None
    novelty_score: Optional[float] = None
    citation_score: Optional[float] = None
    recency_score: Optional[float] = None
    method_signal_score: Optional[float] = None
    impact_proxy_score: Optional[float] = None
    final_score: Optional[float] = None
    rank: Optional[int] = None
    score_breakdown: Optional[Dict[str, float]] = None
    contribution_summary: Optional[str] = None
    method_summary: Optional[str] = None
    brief_summary: Optional[str] = None


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "arxiv-briefing"


def tokenize(value: str) -> List[str]:
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9\-]{2,}", value.lower())
    stop = {
        "the", "and", "for", "with", "from", "that", "this", "are", "was", "were",
        "into", "using", "used", "our", "their", "paper", "study", "results",
        "show", "based", "model", "models", "data", "can", "via", "towards",
    }
    return [word for word in words if word not in stop]


def build_query(topic: str) -> str:
    tokens = tokenize(topic)
    topic_lower = topic.lower()
    if "agentic" in topic_lower or "agent" in topic_lower:
        return '(all:agentic OR all:"ai agent" OR all:"autonomous agent" OR all:"multi-agent" OR all:"llm agent")'
    if "finance" in topic_lower or "financial" in topic_lower:
        return 'all:"artificial intelligence" AND (all:finance OR all:financial OR all:trading OR all:stock)'
    if not tokens:
        return 'all:"artificial intelligence"'
    clauses = [f'all:"{token}"' if "-" not in token else f"all:{token}" for token in tokens[:6]]
    return " AND ".join(clauses)


def ranking_interests(topic: str) -> List[str]:
    tokens = tokenize(topic)
    lower = topic.lower()
    if "agent" in lower or "agentic" in lower:
        tokens.extend(["agentic", "agent", "agents", "multi-agent", "llm", "tool", "planning", "reasoning"])
    if "finance" in lower or "financial" in lower:
        tokens.extend(["finance", "financial", "trading", "stock", "banking", "payment", "market", "risk"])
    if "scientific" in lower or "science" in lower or "discovery" in lower:
        tokens.extend(["scientific", "science", "discovery", "research", "ideation", "experiment", "hypothesis"])
    return tokens


def search_arxiv(query: str, max_results: int) -> List[Paper]:
    encoded = urllib.parse.urlencode(
        {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
    )
    url = f"https://export.arxiv.org/api/query?{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "codex-skill-workflow-test/1.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = response.read()

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }
    root = ET.fromstring(payload)
    papers: List[Paper] = []
    seen = set()

    for entry in root.findall("atom:entry", ns):
        id_url = normalize_text(entry.findtext("atom:id", default="", namespaces=ns))
        paper_id = re.sub(r"v\d+$", "", id_url.rsplit("/", 1)[-1])
        if not paper_id or paper_id in seen:
            continue
        seen.add(paper_id)

        authors = [
            normalize_text(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        ]
        categories = [tag.attrib.get("term", "") for tag in entry.findall("atom:category", ns)]
        primary = entry.find("arxiv:primary_category", ns)
        primary_category = primary.attrib.get("term", categories[0] if categories else "") if primary is not None else ""
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
                break

        papers.append(
            Paper(
                paper_id=paper_id,
                title=normalize_text(entry.findtext("atom:title", default="", namespaces=ns)),
                authors=[a for a in authors if a],
                summary=normalize_text(entry.findtext("atom:summary", default="", namespaces=ns)),
                published=normalize_text(entry.findtext("atom:published", default="", namespaces=ns)),
                updated=normalize_text(entry.findtext("atom:updated", default="", namespaces=ns)),
                url=id_url,
                pdf_url=pdf_url,
                categories=[c for c in categories if c],
                primary_category=primary_category,
            )
        )
    return papers


def rank_papers(papers: List[Paper], interests: List[str]) -> List[Paper]:
    query_tokens = set(tokenize(" ".join(interests)))
    novelty_terms = {
        "novel", "new", "benchmark", "dataset", "framework", "first", "efficient",
        "agentic", "autonomous", "multi-agent", "tool", "planning", "reasoning",
    }
    method_terms = {
        "method", "approach", "framework", "model", "algorithm", "architecture",
        "training", "evaluation", "benchmark", "dataset", "pipeline", "system",
    }
    max_citations = max([p.citation_count or 0 for p in papers] or [0])
    today = parse_run_date(RUN_DATE)

    for paper in papers:
        text = f"{paper.title} {paper.summary} {' '.join(paper.categories)}"
        tokens = tokenize(text)
        counts = Counter(tokens)
        length = max(1, sum(counts.values()))
        overlap = sum(counts[token] for token in query_tokens)
        paper.relevance_score = round(clamp(overlap / math.sqrt(length)), 4)
        paper.novelty_score = round(clamp(sum(counts[t] for t in novelty_terms) / 4), 4)
        paper.method_signal_score = round(clamp(sum(counts[t] for t in method_terms) / 6), 4)

        published = parse_date(paper.published)
        age_days = max(0, (today - published).days) if published else 30
        paper.recency_score = round(clamp(1.0 - safe_ratio(age_days, 30.0)), 4)

        if paper.citation_count is not None and max_citations > 0:
            paper.citation_score = round(math.log1p(paper.citation_count) / math.log1p(max_citations), 4)
        else:
            paper.citation_score = None

        author_signal = clamp(safe_ratio(len(paper.authors), 8))
        category_signal = clamp(safe_ratio(len(set(paper.categories)), 4))
        abstract_signal = clamp(safe_ratio(len(paper.summary), 1200))
        title_signal = 1.0 if any(term in paper.title.lower() for term in ["benchmark", "dataset", "framework", "system"]) else 0.4
        paper.impact_proxy_score = round(mean([author_signal, category_signal, abstract_signal, title_signal]), 4)
        citation_or_proxy = paper.citation_score if paper.citation_score is not None else paper.impact_proxy_score

        weights = {
            "relevance": 0.45,
            "novelty": 0.20,
            "citation_or_proxy": 0.15,
            "recency": 0.10,
            "method_signal": 0.10,
        }
        paper.score_breakdown = {
            "relevance": paper.relevance_score,
            "novelty": paper.novelty_score,
            "citation_score": paper.citation_score if paper.citation_score is not None else 0.0,
            "impact_proxy_score": paper.impact_proxy_score,
            "citation_or_proxy_used": citation_or_proxy,
            "recency": paper.recency_score,
            "method_signal": paper.method_signal_score,
            **{f"weight_{key}": value for key, value in weights.items()},
        }
        paper.final_score = round(
            weights["relevance"] * paper.relevance_score
            + weights["novelty"] * paper.novelty_score
            + weights["citation_or_proxy"] * citation_or_proxy
            + weights["recency"] * paper.recency_score
            + weights["method_signal"] * paper.method_signal_score,
            4,
        )

    ranked = sorted(papers, key=lambda item: (item.final_score or 0, item.published), reverse=True)
    for index, paper in enumerate(ranked, 1):
        paper.rank = index
    return ranked


def first_matching_sentence(sentences: List[str], cues) -> str:
    for sentence in sentences:
        lower = sentence.lower()
        if any(cue in lower for cue in cues):
            return sentence
    return sentences[0] if sentences else ""


def summarize_papers(papers: List[Paper]) -> None:
    contribution_cues = {"propose", "present", "introduce", "develop", "we show", "we demonstrate", "we study"}
    method_cues = {"method", "approach", "framework", "algorithm", "architecture", "training", "model", "agent"}

    for paper in papers:
        sentences = [normalize_text(s) for s in re.split(r"(?<=[.!?])\s+", paper.summary) if normalize_text(s)]
        contribution = first_matching_sentence(sentences, contribution_cues)
        method = first_matching_sentence(sentences, method_cues)
        paper.contribution_summary = contribution
        paper.method_summary = method
        paper.brief_summary = normalize_text(f"{paper.primary_category}: {contribution} Method signal: {method}")


def parse_date(value: str):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(RUN_TZ).date()
    except ValueError:
        return None


def mean(values: List[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    return numerator / denominator if denominator else default


def normalized_entropy(labels: List[str]) -> float:
    counts = Counter(labels)
    if len(counts) <= 1:
        return 1.0 if counts else 0.0
    total = sum(counts.values())
    entropy = -sum((count / total) * math.log(count / total) for count in counts.values())
    return round(entropy / math.log(len(counts)), 4)


def parse_run_date(value: Optional[str] = None):
    try:
        return datetime.fromisoformat((value or RUN_DATE).replace("Z", "+00:00")).date()
    except ValueError:
        return datetime.now(RUN_TZ).date()


def paper_from_dict(data: dict) -> Paper:
    fields = Paper.__dataclass_fields__
    payload = {}
    for name in fields:
        if name == "authors":
            payload[name] = data.get(name) or []
        elif name == "categories":
            payload[name] = data.get(name) or []
        elif name in {
            "paper_id", "title", "summary", "published", "updated",
            "url", "pdf_url", "primary_category",
        }:
            payload[name] = data.get(name) or ""
        else:
            payload[name] = data.get(name)
    return Paper(**payload)


def metric_groups(metrics: Dict[str, float]) -> Dict[str, float]:
    retrieval = mean([
        metrics.get("retrieval_yield_rate", 0.0),
        metrics.get("metadata_completeness_rate", 0.0),
        metrics.get("source_integrity_rate", 0.0),
    ])
    ranking = mean([
        metrics.get("coverage_at_k", 0.0),
        clamp(metrics.get("mean_relevance_score", 0.0)),
        clamp(metrics.get("relevance_lift_at_k", 0.0) / 2.0),
        metrics.get("high_value_rate_at_k", 0.0),
        metrics.get("mean_citation_or_proxy_score", 0.0),
        metrics.get("mean_method_signal_score", 0.0),
    ])
    freshness = mean([
        metrics.get("freshness_at_k", 0.0),
        clamp(1.0 - safe_ratio(metrics.get("recency_days_median", 0.0), 14.0)),
    ])
    diversity = mean([
        clamp(metrics.get("category_diversity", 0.0) / max(1.0, metrics.get("top_k_count", 1.0))),
        metrics.get("category_evenness", 0.0),
    ])
    summary = mean([
        metrics.get("summary_completion_rate", 0.0),
        metrics.get("summary_specificity_score", 0.0),
        metrics.get("brief_actionability_rate", 0.0),
    ])
    integrity = mean([
        metrics.get("link_completeness_rate", 0.0),
        metrics.get("source_integrity_rate", 0.0),
    ])
    visualization = metrics.get("figure_generation_success_rate", 1.0)
    runtime = clamp(1.0 - safe_ratio(metrics.get("runtime_per_paper_seconds", 0.0), 2.0))
    return {
        "retrieval": retrieval,
        "ranking": ranking,
        "freshness": freshness,
        "diversity": diversity,
        "summary": summary,
        "integrity": integrity,
        "visualization": visualization,
        "runtime": runtime,
    }


def compute_metrics(
    papers: List[Paper],
    top_k: int,
    run_started: float,
    stage_times: Dict[str, float],
    max_results: Optional[int] = None,
    run_date: Optional[str] = None,
) -> Dict[str, float]:
    top = papers[:top_k]
    all_relevance = [p.relevance_score or 0.0 for p in papers]
    all_final = [p.final_score or 0.0 for p in papers]
    relevance = [p.relevance_score or 0.0 for p in top]
    novelty = [p.novelty_score or 0.0 for p in top]
    citation_or_proxy = [
        p.citation_score if p.citation_score is not None else (p.impact_proxy_score or 0.0)
        for p in top
    ]
    recency_scores = [p.recency_score or 0.0 for p in top]
    method_scores = [p.method_signal_score or 0.0 for p in top]
    final_scores = [p.final_score or 0.0 for p in top]
    dates = [parse_date(p.published) for p in top]
    today = parse_run_date(run_date)
    ages = [(today - d).days for d in dates if d is not None]
    summary_complete = [
        bool(p.contribution_summary and p.method_summary and p.brief_summary)
        for p in top
    ]
    links_complete = [bool(p.url and p.pdf_url) for p in top]
    metadata_complete = [
        bool(p.paper_id and p.title and p.summary and p.published and p.primary_category and p.url and p.pdf_url)
        for p in papers
    ]
    source_integrity = [
        bool(re.match(r"^\d{4}\.\d{4,5}$", p.paper_id or "") and parse_date(p.published) and p.url and p.pdf_url)
        for p in papers
    ]
    summary_specificity = [
        clamp(
            safe_ratio(len(p.contribution_summary or ""), 220) * 0.35
            + safe_ratio(len(p.method_summary or ""), 220) * 0.35
            + safe_ratio(len(p.brief_summary or ""), 260) * 0.30
        )
        for p in top
    ]
    median_all_relevance = statistics.median(all_relevance) if all_relevance else 0.0
    high_value = [
        1.0 if (p.relevance_score or 0.0) >= median_all_relevance and (p.novelty_score or 0.0) >= 0.25 else 0.0
        for p in top
    ]
    runtime_seconds = round(time.time() - run_started, 3)
    metrics = {
        "retrieved_count": float(len(papers)),
        "top_k_count": float(len(top)),
        "retrieval_yield_rate": round(clamp(safe_ratio(len(papers), max_results or len(papers) or 1)), 4),
        "metadata_completeness_rate": mean([1.0 if value else 0.0 for value in metadata_complete]),
        "source_integrity_rate": mean([1.0 if value else 0.0 for value in source_integrity]),
        "mean_relevance_score": mean(relevance),
        "median_relevance_score": round(statistics.median(relevance), 4) if relevance else 0.0,
        "max_relevance_score": round(max(relevance), 4) if relevance else 0.0,
        "mean_novelty_score": mean(novelty),
        "max_novelty_score": round(max(novelty), 4) if novelty else 0.0,
        "mean_citation_or_proxy_score": mean(citation_or_proxy),
        "real_citation_coverage_rate": mean([1.0 if p.citation_score is not None else 0.0 for p in top]),
        "mean_recency_score": mean(recency_scores),
        "mean_method_signal_score": mean(method_scores),
        "mean_final_score": mean(final_scores),
        "max_final_score": round(max(final_scores), 4) if final_scores else 0.0,
        "relevance_lift_at_k": round(safe_ratio(mean(relevance), mean(all_relevance), 1.0), 4),
        "coverage_at_k": mean([1.0 if score > 0 else 0.0 for score in relevance]),
        "high_value_rate_at_k": mean(high_value),
        "score_spread_at_k": round(statistics.pstdev(final_scores), 4) if len(final_scores) > 1 else 0.0,
        "category_diversity": float(len(set(p.primary_category or "unknown" for p in top))),
        "category_evenness": normalized_entropy([p.primary_category or "unknown" for p in top]),
        "freshness_at_k": mean([1.0 if age <= 7 else 0.0 for age in ages]),
        "recency_days_median": round(statistics.median(ages), 2) if ages else 0.0,
        "summary_completion_rate": mean([1.0 if value else 0.0 for value in summary_complete]),
        "summary_specificity_score": mean(summary_specificity),
        "brief_actionability_rate": mean([1.0 if len(p.brief_summary or "") >= 120 else 0.0 for p in top]),
        "link_completeness_rate": mean([1.0 if value else 0.0 for value in links_complete]),
        "runtime_seconds": runtime_seconds,
        "runtime_per_paper_seconds": round(safe_ratio(runtime_seconds, len(papers)), 4),
        "stage_count": float(len(stage_times)),
    }
    groups = metric_groups(metrics)
    weights = {
        "retrieval": 0.14,
        "ranking": 0.20,
        "freshness": 0.12,
        "diversity": 0.10,
        "summary": 0.16,
        "integrity": 0.12,
        "visualization": 0.08,
        "runtime": 0.08,
    }
    metrics.update({f"{key}_quality_score": round(value, 4) for key, value in groups.items()})
    metrics["overall_quality_score"] = round(sum(groups[key] * weights[key] for key in weights), 4)
    return metrics


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def write_svg(path: Path, body: str, width: int = 1080, height: int = 620) -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <linearGradient id="softBlue" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0%" stop-color="#f7fbff"/>
    <stop offset="100%" stop-color="#eef4f7"/>
  </linearGradient>
  <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
    <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#102033" flood-opacity="0.10"/>
  </filter>
</defs>
<rect width="100%" height="100%" rx="0" fill="{PALETTE['paper']}"/>
{body}
</svg>'''
    path.write_text(svg, encoding="utf-8")


def svg_title(title: str, subtitle: str = "") -> str:
    sub = f'<text x="42" y="72" font-family="Arial" font-size="17" fill="{PALETTE["muted"]}">{esc(subtitle)}</text>' if subtitle else ""
    return f'<text x="42" y="42" font-family="Arial" font-size="26" font-weight="700" fill="{PALETTE["ink"]}">{esc(title)}</text>{sub}'


def svg_card(x: int, y: int, w: int, h: int, fill: str = "url(#softBlue)") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#d9e2ec" filter="url(#shadow)"/>'


def score_color(value: float) -> str:
    if value >= 0.78:
        return PALETTE["green"]
    if value >= 0.58:
        return PALETTE["teal"]
    if value >= 0.38:
        return PALETTE["gold"]
    return PALETTE["rose"]


def quality_groups(metrics: Dict[str, float]) -> List[tuple]:
    return [
        ("Retrieval", metrics.get("retrieval_quality_score", 0.0), PALETTE["blue"]),
        ("Ranking", metrics.get("ranking_quality_score", 0.0), PALETTE["teal"]),
        ("Freshness", metrics.get("freshness_quality_score", 0.0), PALETTE["green"]),
        ("Diversity", metrics.get("diversity_quality_score", 0.0), PALETTE["gold"]),
        ("Summary", metrics.get("summary_quality_score", 0.0), PALETTE["purple"]),
        ("Integrity", metrics.get("integrity_quality_score", 0.0), PALETTE["cyan"]),
        ("Figures", metrics.get("visualization_quality_score", 0.0), PALETTE["orange"]),
        ("Runtime", metrics.get("runtime_quality_score", 0.0), PALETTE["rose"]),
    ]


def evaluation_scorecard(path: Path, metrics: Dict[str, float]) -> None:
    overall = metrics.get("overall_quality_score", 0.0)
    body = [svg_title("Briefing Evaluation Scorecard", "Grouped quality signals for the whole arXiv briefing workflow.")]
    body.append(svg_card(42, 104, 280, 360))
    body.append(f'<text x="72" y="150" font-family="Arial" font-size="15" fill="{PALETTE["muted"]}">Overall quality</text>')
    body.append(f'<text x="72" y="226" font-family="Arial" font-size="62" font-weight="700" fill="{score_color(overall)}">{overall * 100:.0f}</text>')
    body.append(f'<text x="176" y="226" font-family="Arial" font-size="24" fill="{PALETTE["muted"]}">/100</text>')
    body.append(f'<text x="72" y="276" font-family="Arial" font-size="14" fill="{PALETTE["ink"]}">Top-k papers: {int(metrics.get("top_k_count", 0))}</text>')
    body.append(f'<text x="72" y="306" font-family="Arial" font-size="14" fill="{PALETTE["ink"]}">Retrieved: {int(metrics.get("retrieved_count", 0))}</text>')
    body.append(f'<text x="72" y="336" font-family="Arial" font-size="14" fill="{PALETTE["ink"]}">Median age: {metrics.get("recency_days_median", 0):.0f} days</text>')
    body.append(f'<text x="72" y="366" font-family="Arial" font-size="14" fill="{PALETTE["ink"]}">Runtime/paper: {metrics.get("runtime_per_paper_seconds", 0):.2f}s</text>')

    for i, (label, value, color) in enumerate(quality_groups(metrics)):
        col, row = i % 2, i // 2
        x, y = 365 + col * 330, 110 + row * 88
        body.append(svg_card(x, y, 288, 62, "#ffffff"))
        body.append(f'<text x="{x + 20}" y="{y + 25}" font-family="Arial" font-size="14" font-weight="700" fill="{PALETTE["ink"]}">{esc(label)}</text>')
        body.append(f'<rect x="{x + 20}" y="{y + 38}" width="180" height="9" rx="4" fill="#e8eef5"/>')
        body.append(f'<rect x="{x + 20}" y="{y + 38}" width="{int(180 * value)}" height="9" rx="4" fill="{color}"/>')
        body.append(f'<text x="{x + 222}" y="{y + 44}" font-family="Arial" font-size="16" font-weight="700" fill="{score_color(value)}">{value * 100:.0f}</text>')

    details = [
        ("Yield", metrics.get("retrieval_yield_rate", 0.0)),
        ("Lift@K", clamp(metrics.get("relevance_lift_at_k", 0.0) / 2.0)),
        ("Fresh@K", metrics.get("freshness_at_k", 0.0)),
        ("Evenness", metrics.get("category_evenness", 0.0)),
        ("Specificity", metrics.get("summary_specificity_score", 0.0)),
        ("Links", metrics.get("link_completeness_rate", 0.0)),
    ]
    x0, y0 = 365, 490
    for i, (label, value) in enumerate(details):
        x = x0 + i * 108
        body.append(f'<text x="{x}" y="{y0}" font-family="Arial" font-size="12" fill="{PALETTE["muted"]}">{esc(label)}</text>')
        body.append(f'<text x="{x}" y="{y0 + 28}" font-family="Arial" font-size="22" font-weight="700" fill="{score_color(value)}">{value * 100:.0f}</text>')
    write_svg(path, "".join(body), 1080, 560)


def quality_radar(path: Path, metrics: Dict[str, float]) -> None:
    groups = quality_groups(metrics)
    cx, cy, radius = 540, 335, 205
    body = [svg_title("Quality Radar", "A quick view of which part of the pipeline needs attention.")]
    for level in [0.25, 0.5, 0.75, 1.0]:
        points = []
        for idx, _ in enumerate(groups):
            angle = -math.pi / 2 + idx * 2 * math.pi / len(groups)
            points.append(f"{cx + math.cos(angle) * radius * level:.1f},{cy + math.sin(angle) * radius * level:.1f}")
        body.append(f'<polygon points="{" ".join(points)}" fill="none" stroke="{PALETTE["grid"]}" stroke-width="1"/>')
    data_points = []
    for idx, (label, value, color) in enumerate(groups):
        angle = -math.pi / 2 + idx * 2 * math.pi / len(groups)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius
        body.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{PALETTE["grid"]}" stroke-width="1"/>')
        label_x = cx + math.cos(angle) * (radius + 54)
        label_y = cy + math.sin(angle) * (radius + 34)
        anchor = "middle" if abs(math.cos(angle)) < 0.3 else ("start" if math.cos(angle) > 0 else "end")
        body.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" font-family="Arial" font-size="13" font-weight="700" fill="{PALETTE["ink"]}">{esc(label)}</text>')
        body.append(f'<text x="{label_x:.1f}" y="{label_y + 18:.1f}" text-anchor="{anchor}" font-family="Arial" font-size="12" fill="{color}">{value * 100:.0f}</text>')
        data_points.append(f"{cx + math.cos(angle) * radius * value:.1f},{cy + math.sin(angle) * radius * value:.1f}")
    body.append(f'<polygon points="{" ".join(data_points)}" fill="{PALETTE["teal"]}" fill-opacity="0.20" stroke="{PALETTE["teal"]}" stroke-width="3"/>')
    for point in data_points:
        x, y = point.split(",")
        body.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{PALETTE["teal"]}"/>')
    write_svg(path, "".join(body), 1080, 650)


def top_paper_matrix(path: Path, papers: List[Paper], top_k: int, run_date: Optional[str] = None) -> None:
    top = papers[:top_k]
    today = parse_run_date(run_date)
    columns = [
        ("Rel", "relevance_score", PALETTE["blue"]),
        ("Novelty", "novelty_score", PALETTE["gold"]),
        ("Final", "final_score", PALETTE["green"]),
        ("Fresh", "freshness", PALETTE["cyan"]),
        ("Summary", "summary", PALETTE["purple"]),
    ]
    body = [svg_title("Top Paper Quality Matrix", "Each row is a ranked paper; bars show why it appears in the briefing.")]
    x0, y0, row_h = 360, 120, 42
    for i, (label, _, _) in enumerate(columns):
        body.append(f'<text x="{x0 + i * 120}" y="98" font-family="Arial" font-size="13" font-weight="700" fill="{PALETTE["muted"]}">{label}</text>')
    for idx, paper in enumerate(top):
        y = y0 + idx * row_h
        title = f"{paper.rank}. {paper.title[:42]}"
        body.append(f'<text x="42" y="{y + 20}" font-family="Arial" font-size="13" fill="{PALETTE["ink"]}">{esc(title)}</text>')
        age = 999
        date = parse_date(paper.published)
        if date:
            age = max(0, (today - date).days)
        values = {
            "relevance_score": paper.relevance_score or 0.0,
            "novelty_score": paper.novelty_score or 0.0,
            "final_score": paper.final_score or 0.0,
            "freshness": clamp(1.0 - safe_ratio(age, 14.0)),
            "summary": mean([
                1.0 if paper.contribution_summary else 0.0,
                1.0 if paper.method_summary else 0.0,
                1.0 if paper.brief_summary else 0.0,
            ]),
        }
        for col, (_, key, color) in enumerate(columns):
            x = x0 + col * 120
            value = values[key]
            body.append(f'<rect x="{x}" y="{y + 7}" width="86" height="12" rx="6" fill="#e8eef5"/>')
            body.append(f'<rect x="{x}" y="{y + 7}" width="{int(86 * value)}" height="12" rx="6" fill="{color}"/>')
            body.append(f'<text x="{x + 92}" y="{y + 18}" font-family="Arial" font-size="11" fill="{PALETTE["muted"]}">{value:.2f}</text>')
    write_svg(path, "".join(body), 1080, max(620, y0 + len(top) * row_h + 45))


def kpi_cards(path: Path, metrics: Dict[str, float]) -> None:
    cards = [
        ("Retrieved", int(metrics["retrieved_count"])),
        ("Top K", int(metrics["top_k_count"])),
        ("Mean Relevance", f'{metrics["mean_relevance_score"]:.2f}'),
        ("Coverage@K", f'{metrics["coverage_at_k"] * 100:.0f}%'),
        ("Categories", int(metrics["category_diversity"])),
        ("Median Age", f'{metrics["recency_days_median"]:.0f}d'),
        ("Summary Done", f'{metrics["summary_completion_rate"] * 100:.0f}%'),
        ("Links Done", f'{metrics["link_completeness_rate"] * 100:.0f}%'),
    ]
    body = [svg_title("Briefing Evaluation Metrics", "Automatically computed from structured pipeline artifacts.")]
    for i, (label, value) in enumerate(cards):
        col, row = i % 4, i // 4
        x, y = 42 + col * 252, 112 + row * 178
        color = [PALETTE["teal"], PALETTE["blue"], PALETTE["green"], PALETTE["gold"]][col]
        body.append(f'<rect x="{x}" y="{y}" width="222" height="128" rx="8" fill="{PALETTE["panel"]}" stroke="#d7dde8"/>')
        body.append(f'<rect x="{x}" y="{y}" width="8" height="128" rx="4" fill="{color}"/>')
        body.append(f'<text x="{x + 28}" y="{y + 44}" font-family="Arial" font-size="15" fill="{PALETTE["muted"]}">{esc(label)}</text>')
        body.append(f'<text x="{x + 28}" y="{y + 94}" font-family="Arial" font-size="38" font-weight="700" fill="{PALETTE["ink"]}">{esc(value)}</text>')
    write_svg(path, "".join(body), 1080, 460)


def category_chart(path: Path, papers: List[Paper], top_k: int) -> None:
    counts = Counter(p.primary_category or "unknown" for p in papers[:top_k])
    items = counts.most_common()
    max_value = max([v for _, v in items] or [1])
    total = sum(counts.values()) or 1
    body = [svg_title("Category Distribution", "Primary arXiv categories among top-ranked papers.")]
    chart_x, chart_y, chart_w = 162, 116, 760
    for idx, (label, value) in enumerate(items):
        y = chart_y + idx * 52
        width = int(chart_w * value / max_value)
        color = [PALETTE["blue"], PALETTE["teal"], PALETTE["green"], PALETTE["gold"], PALETTE["purple"], PALETTE["rose"]][idx % 6]
        body.append(svg_card(42, y - 8, 970, 42, "#ffffff"))
        body.append(f'<text x="64" y="{y + 18}" font-family="Arial" font-size="15" font-weight="700" fill="{PALETTE["ink"]}">{esc(label)}</text>')
        body.append(f'<rect x="{chart_x}" y="{y + 4}" width="{chart_w}" height="16" rx="8" fill="#e8eef5"/>')
        body.append(f'<rect x="{chart_x}" y="{y + 4}" width="{width}" height="16" rx="8" fill="{color}"/>')
        body.append(f'<text x="{chart_x + chart_w + 18}" y="{y + 18}" font-family="Arial" font-size="14" fill="{PALETTE["ink"]}">{value} ({value / total * 100:.0f}%)</text>')
    write_svg(path, "".join(body), 1080, max(340, chart_y + len(items) * 52 + 45))


def score_chart(path: Path, papers: List[Paper], top_k: int) -> None:
    top = papers[:top_k]
    body = [svg_title("Top Papers: Relevance, Novelty, Final Score", "Scores are normalized to 0-1 and sorted by fused final score.")]
    x0, y0, chart_w, row_h = 380, 114, 570, 42
    colors = [(PALETTE["blue"], "rel"), (PALETTE["gold"], "nov"), (PALETTE["green"], "final")]
    for idx, paper in enumerate(top):
        y = y0 + idx * row_h
        label = f"{paper.rank}. {paper.title[:44]}"
        body.append(f'<text x="42" y="{y + 20}" font-family="Arial" font-size="13" fill="{PALETTE["ink"]}">{esc(label)}</text>')
        for offset, (color, attr) in enumerate(colors):
            score = getattr(paper, {"rel": "relevance_score", "nov": "novelty_score", "final": "final_score"}[attr]) or 0
            width = int(chart_w * score)
            body.append(f'<rect x="{x0}" y="{y + offset * 11}" width="{chart_w}" height="8" fill="#edf1f5"/>')
            body.append(f'<rect x="{x0}" y="{y + offset * 11}" width="{width}" height="8" fill="{color}"/>')
    legend_x = 785
    for i, (color, label) in enumerate([(PALETTE["blue"], "Relevance"), (PALETTE["gold"], "Novelty"), (PALETTE["green"], "Final")]):
        body.append(f'<rect x="{legend_x}" y="{62 + i * 18}" width="12" height="12" fill="{color}"/>')
        body.append(f'<text x="{legend_x + 18}" y="{72 + i * 18}" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">{label}</text>')
    write_svg(path, "".join(body), 1080, max(600, y0 + len(top) * row_h + 40))


def recency_scatter(path: Path, papers: List[Paper], top_k: int) -> None:
    top = papers[:top_k]
    today = datetime.now(RUN_TZ).date()
    points = []
    for paper in top:
        date = parse_date(paper.published)
        if date is not None:
            points.append((paper, max(0, (today - date).days), paper.relevance_score or 0.0, paper.final_score or 0.0))
    max_age = max([age for _, age, _, _ in points] or [1])
    body = [svg_title("Relevance vs. Recency", "Higher points are more relevant; left side is more recent; larger points have higher final score.")]
    x0, y0, w, h = 92, 118, 880, 380
    body.append(f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{PALETTE["ink"]}"/>')
    body.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{PALETTE["ink"]}"/>')
    for i in range(6):
        y = y0 + h - i * h / 5
        body.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{PALETTE["grid"]}" stroke-dasharray="4 6"/>')
        body.append(f'<text x="48" y="{y + 4}" font-family="Arial" font-size="12" fill="{PALETTE["muted"]}">{i / 5:.1f}</text>')
    for paper, age, score, final_score in points:
        x = x0 + int(w * (age / max_age if max_age else 0))
        y = y0 + h - int(h * score)
        radius = 6 + int(10 * final_score)
        body.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{score_color(final_score)}" opacity="0.80" stroke="#ffffff" stroke-width="2"/>')
        body.append(f'<text x="{x + 10}" y="{y + 4}" font-family="Arial" font-size="11" fill="{PALETTE["ink"]}">{esc(paper.paper_id)}</text>')
    body.append(f'<text x="{x0 + w - 120}" y="{y0 + h + 42}" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">Age in days</text>')
    body.append(f'<text x="28" y="{y0 - 14}" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">Relevance</text>')
    write_svg(path, "".join(body), 1080, 580)


def histogram_chart(path: Path, papers: List[Paper], top_k: int) -> None:
    bins = [0, 0, 0, 0, 0]
    novelty_bins = [0, 0, 0, 0, 0]
    final_bins = [0, 0, 0, 0, 0]
    for paper in papers[:top_k]:
        rel = min(4, int((paper.relevance_score or 0) * 5))
        nov = min(4, int((paper.novelty_score or 0) * 5))
        final = min(4, int((paper.final_score or 0) * 5))
        bins[rel] += 1
        novelty_bins[nov] += 1
        final_bins[final] += 1
    body = [svg_title("Score Distribution", "Relevance, novelty, and fused final score counts by score band.")]
    x0, y0, w, h = 100, 122, 800, 340
    max_value = max(bins + novelty_bins + final_bins + [1])
    labels = ["0-.2", ".2-.4", ".4-.6", ".6-.8", ".8-1"]
    for i, label in enumerate(labels):
        x = x0 + i * 150
        rel_h = int(h * bins[i] / max_value)
        nov_h = int(h * novelty_bins[i] / max_value)
        fin_h = int(h * final_bins[i] / max_value)
        body.append(f'<rect x="{x}" y="{y0 + h - rel_h}" width="30" height="{rel_h}" rx="4" fill="{PALETTE["blue"]}"/>')
        body.append(f'<rect x="{x + 38}" y="{y0 + h - nov_h}" width="30" height="{nov_h}" rx="4" fill="{PALETTE["gold"]}"/>')
        body.append(f'<rect x="{x + 76}" y="{y0 + h - fin_h}" width="30" height="{fin_h}" rx="4" fill="{PALETTE["green"]}"/>')
        body.append(f'<text x="{x + 8}" y="{y0 + h + 28}" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">{label}</text>')
    body.append(f'<line x1="{x0 - 10}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{PALETTE["ink"]}"/>')
    body.append(f'<rect x="742" y="62" width="12" height="12" fill="{PALETTE["blue"]}"/><text x="762" y="73" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">Relevance</text>')
    body.append(f'<rect x="742" y="84" width="12" height="12" fill="{PALETTE["gold"]}"/><text x="762" y="95" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">Novelty</text>')
    body.append(f'<rect x="742" y="106" width="12" height="12" fill="{PALETTE["green"]}"/><text x="762" y="117" font-family="Arial" font-size="13" fill="{PALETTE["muted"]}">Final</text>')
    write_svg(path, "".join(body), 1080, 560)


def summary_coverage_chart(path: Path, papers: List[Paper], top_k: int) -> None:
    top = papers[:top_k]
    fields = [
        ("Contribution", "contribution_summary", PALETTE["teal"]),
        ("Method", "method_summary", PALETTE["purple"]),
        ("Brief", "brief_summary", PALETTE["green"]),
    ]
    body = [svg_title("Summary Field Coverage", "Completion rate for generated paper summaries.")]
    for i, (label, field, color) in enumerate(fields):
        rate = mean([1.0 if getattr(p, field) else 0.0 for p in top])
        x, y = 240, 145 + i * 96
        body.append(f'<text x="70" y="{y + 25}" font-family="Arial" font-size="18" fill="{PALETTE["ink"]}">{label}</text>')
        body.append(f'<rect x="{x}" y="{y}" width="650" height="34" rx="4" fill="#edf1f5"/>')
        body.append(f'<rect x="{x}" y="{y}" width="{int(650 * rate)}" height="34" rx="4" fill="{color}"/>')
        body.append(f'<text x="920" y="{y + 24}" font-family="Arial" font-size="18" font-weight="700" fill="{PALETTE["ink"]}">{rate * 100:.0f}%</text>')
    write_svg(path, "".join(body), 1080, 500)


def summary_quality_chart(path: Path, papers: List[Paper], top_k: int, metrics: Dict[str, float]) -> None:
    top = papers[:top_k]
    body = [svg_title("Summary Quality", "Completion, specificity, and skimmability of generated paper summaries.")]
    indicators = [
        ("Completion", metrics.get("summary_completion_rate", 0.0), PALETTE["green"]),
        ("Specificity", metrics.get("summary_specificity_score", 0.0), PALETTE["purple"]),
        ("Actionability", metrics.get("brief_actionability_rate", 0.0), PALETTE["teal"]),
    ]
    for i, (label, value, color) in enumerate(indicators):
        x = 84 + i * 315
        body.append(svg_card(x, 118, 250, 140, "#ffffff"))
        body.append(f'<text x="{x + 22}" y="154" font-family="Arial" font-size="15" font-weight="700" fill="{PALETTE["ink"]}">{label}</text>')
        body.append(f'<text x="{x + 22}" y="215" font-family="Arial" font-size="42" font-weight="700" fill="{color}">{value * 100:.0f}%</text>')
        body.append(f'<rect x="{x + 22}" y="232" width="198" height="10" rx="5" fill="#e8eef5"/>')
        body.append(f'<rect x="{x + 22}" y="232" width="{int(198 * value)}" height="10" rx="5" fill="{color}"/>')

    fields = [
        ("Contribution", "contribution_summary", PALETTE["blue"]),
        ("Method", "method_summary", PALETTE["gold"]),
        ("Brief", "brief_summary", PALETTE["green"]),
    ]
    for i, (label, field, color) in enumerate(fields):
        rate = mean([1.0 if getattr(p, field) else 0.0 for p in top])
        x, y = 190, 326 + i * 58
        body.append(f'<text x="70" y="{y + 19}" font-family="Arial" font-size="15" fill="{PALETTE["ink"]}">{label}</text>')
        body.append(f'<rect x="{x}" y="{y}" width="700" height="22" rx="11" fill="#e8eef5"/>')
        body.append(f'<rect x="{x}" y="{y}" width="{int(700 * rate)}" height="22" rx="11" fill="{color}"/>')
        body.append(f'<text x="916" y="{y + 18}" font-family="Arial" font-size="14" font-weight="700" fill="{PALETTE["ink"]}">{rate * 100:.0f}%</text>')
    write_svg(path, "".join(body), 1080, 560)


def runtime_chart(path: Path, stage_times: Dict[str, float]) -> None:
    items = list(stage_times.items())
    max_value = max([v for _, v in items] or [1])
    if max_value <= 0:
        max_value = 1.0
    body = [svg_title("Runtime by Stage", "Wall-clock seconds measured during this test run.")]
    for idx, (label, value) in enumerate(items):
        y = 126 + idx * 62
        width = int(760 * value / max_value)
        body.append(f'<text x="64" y="{y + 22}" font-family="Arial" font-size="16" fill="{PALETTE["ink"]}">{esc(label)}</text>')
        body.append(f'<rect x="250" y="{y}" width="760" height="30" fill="#edf1f5"/>')
        body.append(f'<rect x="250" y="{y}" width="{width}" height="30" fill="{PALETTE["blue"]}"/>')
        body.append(f'<text x="{260 + width}" y="{y + 22}" font-family="Arial" font-size="14" fill="{PALETTE["ink"]}">{value:.2f}s</text>')
    write_svg(path, "".join(body), 1080, 480)


def rgb(hex_color: str):
    value = hex_color.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def pil_font(size: int, bold: bool = False):
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> List[str]:
    words = str(text).split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if text_size(draw, candidate, font)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def png_canvas(width: int = 1080, height: int = 640):
    image = Image.new("RGB", (width, height), rgb(PALETTE["paper"]))
    draw = ImageDraw.Draw(image)
    return image, draw


def png_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str = "") -> None:
    draw.text((42, 28), title, fill=rgb(PALETTE["ink"]), font=pil_font(28, True))
    if subtitle:
        draw.text((42, 66), subtitle, fill=rgb(PALETTE["muted"]), font=pil_font(16))


def png_card(draw: ImageDraw.ImageDraw, xy, fill: str = "#ffffff", outline: str = "#d9e2ec") -> None:
    draw.rounded_rectangle(xy, radius=14, fill=rgb(fill), outline=rgb(outline), width=1)


def png_bar(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, value: float, color: str) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=rgb("#e8eef5"))
    draw.rounded_rectangle((x, y, x + int(w * clamp(value)), y + h), radius=h // 2, fill=rgb(color))


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True)


def png_evaluation_scorecard(path: Path, metrics: Dict[str, float]) -> None:
    image, draw = png_canvas(1080, 600)
    png_title(draw, "Briefing Evaluation Scorecard", "Grouped quality signals for the full arXiv briefing workflow.")
    overall = metrics.get("overall_quality_score", 0.0)
    png_card(draw, (42, 112, 326, 484), PALETTE["panel"])
    draw.text((72, 148), "Overall quality", fill=rgb(PALETTE["muted"]), font=pil_font(16, True))
    draw.text((72, 205), f"{overall * 100:.0f}", fill=rgb(score_color(overall)), font=pil_font(70, True))
    draw.text((185, 244), "/100", fill=rgb(PALETTE["muted"]), font=pil_font(24))
    left_metrics = [
        f"Top-k papers: {int(metrics.get('top_k_count', 0))}",
        f"Retrieved: {int(metrics.get('retrieved_count', 0))}",
        f"Median age: {metrics.get('recency_days_median', 0):.0f} days",
        f"Runtime/paper: {metrics.get('runtime_per_paper_seconds', 0):.2f}s",
        f"Real citation coverage: {metrics.get('real_citation_coverage_rate', 0) * 100:.0f}%",
    ]
    for i, line in enumerate(left_metrics):
        draw.text((72, 318 + i * 30), line, fill=rgb(PALETTE["ink"]), font=pil_font(15))

    for i, (label, value, color) in enumerate(quality_groups(metrics)):
        col, row = i % 2, i // 2
        x, y = 370 + col * 325, 118 + row * 94
        png_card(draw, (x, y, x + 292, y + 68))
        draw.text((x + 18, y + 14), label, fill=rgb(PALETTE["ink"]), font=pil_font(15, True))
        png_bar(draw, x + 18, y + 42, 190, 12, value, color)
        draw.text((x + 224, y + 31), f"{value * 100:.0f}", fill=rgb(score_color(value)), font=pil_font(22, True))
    save_png(image, path)


def png_quality_radar(path: Path, metrics: Dict[str, float]) -> None:
    image, draw = png_canvas(1080, 700)
    png_title(draw, "Quality Radar", "Eight grouped scores reveal the weakest stage at a glance.")
    groups = quality_groups(metrics)
    cx, cy, radius = 540, 390, 220
    for level in [0.25, 0.5, 0.75, 1.0]:
        pts = []
        for idx, _ in enumerate(groups):
            angle = -math.pi / 2 + idx * 2 * math.pi / len(groups)
            pts.append((cx + math.cos(angle) * radius * level, cy + math.sin(angle) * radius * level))
        draw.line(pts + [pts[0]], fill=rgb(PALETTE["grid"]), width=1)
    data_pts = []
    for idx, (label, value, color) in enumerate(groups):
        angle = -math.pi / 2 + idx * 2 * math.pi / len(groups)
        end = (cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
        draw.line((cx, cy, end[0], end[1]), fill=rgb(PALETTE["grid"]), width=1)
        data_pts.append((cx + math.cos(angle) * radius * value, cy + math.sin(angle) * radius * value))
        lx, ly = cx + math.cos(angle) * (radius + 58), cy + math.sin(angle) * (radius + 42)
        label_w = text_size(draw, label, pil_font(13, True))[0]
        draw.text((lx - label_w / 2, ly - 10), label, fill=rgb(PALETTE["ink"]), font=pil_font(13, True))
        score = f"{value * 100:.0f}"
        score_w = text_size(draw, score, pil_font(12))[0]
        draw.text((lx - score_w / 2, ly + 10), score, fill=rgb(color), font=pil_font(12))
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.polygon(data_pts, fill=(47, 125, 126, 64), outline=rgb(PALETTE["teal"]) + (255,))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.line(data_pts + [data_pts[0]], fill=rgb(PALETTE["teal"]), width=3)
    for x, y in data_pts:
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=rgb(PALETTE["teal"]))
    save_png(image, path)


def png_top_paper_matrix(path: Path, papers: List[Paper], top_k: int, run_date: Optional[str] = None) -> None:
    top = papers[:top_k]
    height = max(680, 130 + len(top) * 44)
    image, draw = png_canvas(1240, height)
    png_title(draw, "Top Paper Quality Matrix", "Bars explain each selected paper across ranking dimensions.")
    today = parse_run_date(run_date)
    columns = [
        ("Rel", "relevance_score", PALETTE["blue"]),
        ("Nov", "novelty_score", PALETTE["gold"]),
        ("Cite/Proxy", "citation_or_proxy", PALETTE["orange"]),
        ("Recent", "recency_score", PALETTE["cyan"]),
        ("Method", "method_signal_score", PALETTE["purple"]),
        ("Final", "final_score", PALETTE["green"]),
        ("Summary", "summary", PALETTE["teal"]),
    ]
    x0, y0, row_h = 395, 120, 44
    for i, (label, _, _) in enumerate(columns):
        draw.text((x0 + i * 112, 94), label, fill=rgb(PALETTE["muted"]), font=pil_font(13, True))
    for idx, paper in enumerate(top):
        y = y0 + idx * row_h
        fill = "#ffffff" if idx % 2 == 0 else PALETTE["panel"]
        draw.rounded_rectangle((32, y - 8, 1205, y + 30), radius=8, fill=rgb(fill))
        label = f"{paper.rank}. {paper.title[:48]}"
        draw.text((48, y), label, fill=rgb(PALETTE["ink"]), font=pil_font(13))
        cite_or_proxy = paper.citation_score if paper.citation_score is not None else (paper.impact_proxy_score or 0.0)
        summary_ready = mean([
            1.0 if paper.contribution_summary else 0.0,
            1.0 if paper.method_summary else 0.0,
            1.0 if paper.brief_summary else 0.0,
        ])
        values = {
            "relevance_score": paper.relevance_score or 0.0,
            "novelty_score": paper.novelty_score or 0.0,
            "citation_or_proxy": cite_or_proxy,
            "recency_score": paper.recency_score or 0.0,
            "method_signal_score": paper.method_signal_score or 0.0,
            "final_score": paper.final_score or 0.0,
            "summary": summary_ready,
        }
        for col, (_, key, color) in enumerate(columns):
            x = x0 + col * 112
            value = values[key]
            png_bar(draw, x, y + 4, 74, 10, value, color)
            draw.text((x + 80, y - 1), f"{value:.2f}", fill=rgb(PALETTE["muted"]), font=pil_font(10))
    save_png(image, path)


def png_category_distribution(path: Path, papers: List[Paper], top_k: int) -> None:
    counts = Counter(p.primary_category or "unknown" for p in papers[:top_k])
    items = counts.most_common()
    height = max(430, 130 + len(items) * 58)
    image, draw = png_canvas(1080, height)
    png_title(draw, "Category Distribution", "Primary arXiv categories among top-ranked papers.")
    max_value = max([v for _, v in items] or [1])
    total = sum(counts.values()) or 1
    for idx, (label, value) in enumerate(items):
        y = 126 + idx * 58
        png_card(draw, (48, y - 8, 1010, y + 40))
        draw.text((68, y + 7), label, fill=rgb(PALETTE["ink"]), font=pil_font(15, True))
        color = [PALETTE["blue"], PALETTE["teal"], PALETTE["green"], PALETTE["gold"], PALETTE["purple"], PALETTE["rose"]][idx % 6]
        png_bar(draw, 170, y + 10, 660, 16, value / max_value, color)
        draw.text((850, y + 7), f"{value} ({value / total * 100:.0f}%)", fill=rgb(PALETTE["ink"]), font=pil_font(14))
    save_png(image, path)


def png_relevance_recency(path: Path, papers: List[Paper], top_k: int, run_date: Optional[str] = None) -> None:
    image, draw = png_canvas(1080, 640)
    png_title(draw, "Relevance vs. Recency", "Higher is more relevant; left is fresher; point color indicates final score.")
    today = parse_run_date(run_date)
    points = []
    for paper in papers[:top_k]:
        date = parse_date(paper.published)
        if date:
            points.append((paper, max(0, (today - date).days), paper.relevance_score or 0.0, paper.final_score or 0.0))
    max_age = max([age for _, age, _, _ in points] or [1])
    x0, y0, w, h = 92, 122, 860, 390
    draw.line((x0, y0 + h, x0 + w, y0 + h), fill=rgb(PALETTE["ink"]), width=2)
    draw.line((x0, y0, x0, y0 + h), fill=rgb(PALETTE["ink"]), width=2)
    for i in range(6):
        y = y0 + h - i * h / 5
        draw.line((x0, y, x0 + w, y), fill=rgb(PALETTE["grid"]), width=1)
        draw.text((46, y - 8), f"{i / 5:.1f}", fill=rgb(PALETTE["muted"]), font=pil_font(12))
    for paper, age, rel, final in points:
        x = x0 + int(w * safe_ratio(age, max_age))
        y = y0 + h - int(h * rel)
        r = 7 + int(9 * final)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=rgb(score_color(final)), outline=rgb("#ffffff"), width=2)
        draw.text((x + r + 3, y - 7), paper.paper_id, fill=rgb(PALETTE["ink"]), font=pil_font(10))
    draw.text((x0 + w - 110, y0 + h + 36), "Age in days", fill=rgb(PALETTE["muted"]), font=pil_font(13))
    draw.text((28, y0 - 20), "Relevance", fill=rgb(PALETTE["muted"]), font=pil_font(13))
    save_png(image, path)


def png_score_distribution(path: Path, papers: List[Paper], top_k: int) -> None:
    image, draw = png_canvas(1080, 610)
    png_title(draw, "Score Distribution", "Counts by score band across ranking dimensions.")
    keys = [
        ("Rel", "relevance_score", PALETTE["blue"]),
        ("Nov", "novelty_score", PALETTE["gold"]),
        ("Cite/Proxy", "citation_or_proxy", PALETTE["orange"]),
        ("Method", "method_signal_score", PALETTE["purple"]),
        ("Final", "final_score", PALETTE["green"]),
    ]
    labels = ["0-.2", ".2-.4", ".4-.6", ".6-.8", ".8-1"]
    bins = {name: [0, 0, 0, 0, 0] for name, _, _ in keys}
    for paper in papers[:top_k]:
        values = {
            "relevance_score": paper.relevance_score or 0.0,
            "novelty_score": paper.novelty_score or 0.0,
            "citation_or_proxy": paper.citation_score if paper.citation_score is not None else (paper.impact_proxy_score or 0.0),
            "method_signal_score": paper.method_signal_score or 0.0,
            "final_score": paper.final_score or 0.0,
        }
        for name, key, _ in keys:
            bins[name][min(4, int(values[key] * 5))] += 1
    max_value = max([count for values in bins.values() for count in values] + [1])
    x0, y0, h = 100, 140, 330
    for band, label in enumerate(labels):
        base_x = x0 + band * 170
        for idx, (name, _, color) in enumerate(keys):
            bar_h = int(h * bins[name][band] / max_value)
            x = base_x + idx * 24
            draw.rounded_rectangle((x, y0 + h - bar_h, x + 18, y0 + h), radius=4, fill=rgb(color))
        draw.text((base_x, y0 + h + 24), label, fill=rgb(PALETTE["muted"]), font=pil_font(13))
    draw.line((x0 - 12, y0 + h, 960, y0 + h), fill=rgb(PALETTE["ink"]), width=2)
    for idx, (name, _, color) in enumerate(keys):
        x = 710 + (idx % 2) * 150
        y = 76 + (idx // 2) * 24
        draw.rectangle((x, y, x + 12, y + 12), fill=rgb(color))
        draw.text((x + 18, y - 2), name, fill=rgb(PALETTE["muted"]), font=pil_font(12))
    save_png(image, path)


def png_summary_quality(path: Path, papers: List[Paper], top_k: int, metrics: Dict[str, float]) -> None:
    image, draw = png_canvas(1080, 580)
    png_title(draw, "Summary Quality", "Completion, specificity, and skimmability of generated summaries.")
    indicators = [
        ("Completion", metrics.get("summary_completion_rate", 0.0), PALETTE["green"]),
        ("Specificity", metrics.get("summary_specificity_score", 0.0), PALETTE["purple"]),
        ("Actionability", metrics.get("brief_actionability_rate", 0.0), PALETTE["teal"]),
    ]
    for i, (label, value, color) in enumerate(indicators):
        x = 82 + i * 318
        png_card(draw, (x, 120, x + 255, 260))
        draw.text((x + 24, 154), label, fill=rgb(PALETTE["ink"]), font=pil_font(15, True))
        draw.text((x + 24, 198), f"{value * 100:.0f}%", fill=rgb(color), font=pil_font(38, True))
        png_bar(draw, x + 24, 236, 198, 10, value, color)
    top = papers[:top_k]
    fields = [
        ("Contribution", "contribution_summary", PALETTE["blue"]),
        ("Method", "method_summary", PALETTE["gold"]),
        ("Brief", "brief_summary", PALETTE["green"]),
    ]
    for i, (label, field, color) in enumerate(fields):
        rate = mean([1.0 if getattr(p, field) else 0.0 for p in top])
        y = 326 + i * 60
        draw.text((72, y + 2), label, fill=rgb(PALETTE["ink"]), font=pil_font(15))
        png_bar(draw, 198, y + 5, 690, 20, rate, color)
        draw.text((912, y + 2), f"{rate * 100:.0f}%", fill=rgb(PALETTE["ink"]), font=pil_font(15, True))
    save_png(image, path)


def png_runtime_by_stage(path: Path, stage_times: Dict[str, float]) -> None:
    image, draw = png_canvas(1080, 500)
    png_title(draw, "Runtime by Stage", "Wall-clock seconds measured during this test run.")
    items = list(stage_times.items())
    max_value = max([float(v) for _, v in items] + [1.0])
    if max_value <= 0:
        max_value = 1.0
    for idx, (label, value) in enumerate(items):
        y = 126 + idx * 60
        draw.text((64, y + 4), label, fill=rgb(PALETTE["ink"]), font=pil_font(15, True))
        png_bar(draw, 252, y + 8, 720, 22, float(value) / max_value, PALETTE["blue"])
        draw.text((985, y + 4), f"{float(value):.2f}s", fill=rgb(PALETTE["muted"]), font=pil_font(13))
    save_png(image, path)


def write_visualizations(
    papers: List[Paper],
    figure_dir: Path,
    metrics: Dict[str, float],
    stage_times: Dict[str, float],
    top_k: int,
    run_date: Optional[str] = None,
) -> List[dict]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    figures = [
        ("evaluation_scorecard", "evaluation_scorecard.png", "Grouped quality scorecard for the full briefing workflow.", "Scorecard with overall and grouped quality scores.", "overview"),
        ("quality_radar", "quality_radar.png", "Radar chart showing strengths and weaknesses across evaluation groups.", "Radar chart of retrieval, ranking, freshness, diversity, summary, integrity, figure, and runtime scores.", "radar"),
        ("top_paper_matrix", "top_paper_matrix.png", "Top paper matrix showing why each paper was selected.", "Matrix of relevance, novelty, citation/proxy, recency, method signal, final score, and summary readiness for ranked papers.", "matrix"),
        ("category_distribution", "category_distribution.png", "Primary category distribution for top ranked papers.", "Horizontal bar chart of primary arXiv categories.", "bar"),
        ("relevance_recency", "relevance_recency.png", "Relationship between paper recency, relevance, and final score.", "Scatter plot of relevance score against age in days, with point size indicating final score.", "scatter"),
        ("score_distribution", "score_distribution.png", "Distribution of relevance, novelty, citation/proxy, method, and final scores.", "Histogram of score bands for each ranking dimension.", "histogram"),
        ("summary_quality", "summary_quality.png", "Summary completion, specificity, and actionability.", "Summary quality chart with completion and usefulness indicators.", "coverage"),
        ("runtime_by_stage", "runtime_by_stage.png", "Measured runtime for each workflow stage.", "Runtime bar chart split by workflow stage.", "runtime"),
    ]
    png_evaluation_scorecard(figure_dir / "evaluation_scorecard.png", metrics)
    png_quality_radar(figure_dir / "quality_radar.png", metrics)
    png_top_paper_matrix(figure_dir / "top_paper_matrix.png", papers, top_k, run_date)
    png_category_distribution(figure_dir / "category_distribution.png", papers, top_k)
    png_relevance_recency(figure_dir / "relevance_recency.png", papers, top_k, run_date)
    png_score_distribution(figure_dir / "score_distribution.png", papers, top_k)
    png_summary_quality(figure_dir / "summary_quality.png", papers, top_k, metrics)
    png_runtime_by_stage(figure_dir / "runtime_by_stage.png", stage_times)
    return [
        {
            "figure_id": figure_id,
            "path": f"figures/{filename}",
            "caption": caption,
            "alt_text": alt_text,
            "kind": kind,
            "width": 1240 if figure_id == "top_paper_matrix" else 1080,
        }
        for figure_id, filename, caption, alt_text, kind in figures
    ]


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(path: Path, papers: List[Paper], top_k: int) -> None:
    columns = [
        "rank", "paper_id", "title", "published", "primary_category",
        "relevance_score", "novelty_score", "citation_count", "citation_score",
        "impact_proxy_score", "recency_score", "method_signal_score", "final_score",
        "brief_summary", "url", "pdf_url",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for paper in papers[:top_k]:
            row = asdict(paper)
            writer.writerow({key: row.get(key) for key in columns})


def write_markdown(path: Path, topic: str, query: str, papers: List[Paper], figures: List[dict], metrics: Dict[str, float], warnings: List[str], top_k: int) -> None:
    lines = [
        f"# Daily arXiv Briefing: {topic} ({RUN_DATE})",
        "",
        "## Executive Summary",
        f"Retrieved {int(metrics['retrieved_count'])} recent arXiv papers and selected the top {int(metrics['top_k_count'])} for `{topic}`.",
        f"The arXiv query was `{query}`. Top-k coverage is {metrics['coverage_at_k'] * 100:.0f}% and median recency is {metrics['recency_days_median']:.0f} days.",
        "",
        "## Evaluation Metrics",
        "| Metric | Value |",
        "|---|---:|",
        f"| Retrieved papers | {int(metrics['retrieved_count'])} |",
        f"| Top-k papers | {int(metrics['top_k_count'])} |",
        f"| Overall quality score | {metrics['overall_quality_score'] * 100:.0f}/100 |",
        f"| Retrieval yield | {metrics['retrieval_yield_rate'] * 100:.0f}% |",
        f"| Metadata completeness | {metrics['metadata_completeness_rate'] * 100:.0f}% |",
        f"| Mean relevance | {metrics['mean_relevance_score']:.3f} |",
        f"| Max relevance | {metrics['max_relevance_score']:.3f} |",
        f"| Relevance lift at k | {metrics['relevance_lift_at_k']:.2f}x |",
        f"| High-value rate at k | {metrics['high_value_rate_at_k'] * 100:.0f}% |",
        f"| Mean novelty | {metrics['mean_novelty_score']:.3f} |",
        f"| Mean citation/proxy score | {metrics['mean_citation_or_proxy_score']:.3f} |",
        f"| Real citation coverage | {metrics['real_citation_coverage_rate'] * 100:.0f}% |",
        f"| Mean recency score | {metrics['mean_recency_score']:.3f} |",
        f"| Mean method signal | {metrics['mean_method_signal_score']:.3f} |",
        f"| Coverage at k | {metrics['coverage_at_k'] * 100:.0f}% |",
        f"| Category diversity | {int(metrics['category_diversity'])} |",
        f"| Category evenness | {metrics['category_evenness']:.3f} |",
        f"| Freshness at k | {metrics['freshness_at_k'] * 100:.0f}% |",
        f"| Median recency | {metrics['recency_days_median']:.0f} days |",
        f"| Summary completion | {metrics['summary_completion_rate'] * 100:.0f}% |",
        f"| Summary specificity | {metrics['summary_specificity_score'] * 100:.0f}% |",
        f"| Brief actionability | {metrics['brief_actionability_rate'] * 100:.0f}% |",
        f"| Link completeness | {metrics['link_completeness_rate'] * 100:.0f}% |",
        f"| Figure generation success | {metrics['figure_generation_success_rate'] * 100:.0f}% |",
        f"| Runtime per paper | {metrics['runtime_per_paper_seconds']:.2f}s |",
        "",
        "## Visual Overview",
    ]
    for figure in figures:
        lines.extend([
            f"![{figure['alt_text']}]({figure['path']})",
            f"*{figure['caption']}*",
            "",
        ])

    lines.extend([
        "## Summary Table",
        "| Rank | Title | arXiv | Rel | Nov | Cite/Proxy | Recency | Method | Final | Category | Published | Links |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ])
    for paper in papers[:top_k]:
        title = paper.title.replace("|", "\\|")
        cite_or_proxy = paper.citation_score if paper.citation_score is not None else (paper.impact_proxy_score or 0.0)
        lines.append(
            f"| {paper.rank} | {title} | {paper.paper_id} | {paper.relevance_score:.3f} | "
            f"{paper.novelty_score:.3f} | {cite_or_proxy:.3f} | {paper.recency_score:.3f} | "
            f"{paper.method_signal_score:.3f} | {paper.final_score:.3f} | {paper.primary_category} | {paper.published[:10]} | "
            f"[abs]({paper.url}) / [pdf]({paper.pdf_url}) |"
        )

    lines.extend(["", "## Highlighted Papers"])
    for paper in papers[: min(5, top_k)]:
        lines.extend(
            [
                f"### {paper.rank}. {paper.title}",
                f"- Authors: {', '.join(paper.authors[:6])}",
                f"- Contribution: {paper.contribution_summary}",
                f"- Method: {paper.method_summary}",
                f"- Brief: {paper.brief_summary}",
                "",
            ]
        )

    lines.extend(["## Notes"])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No blocking workflow warnings.")
    lines.append("- Citation/proxy score uses real citation counts only when `citation_count` is present; otherwise it uses a labeled impact proxy from metadata and abstract signals.")
    lines.append(f"- Output generated on {RUN_DATE} using UTC+8 date boundaries.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(topic: str, max_results: int, top_k: int, query_override: Optional[str] = None) -> int:
    run_started = time.time()
    warnings: List[str] = []
    output = ROOT / "outputs" / slugify(topic)
    figure_dir = output / "figures"
    output.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(exist_ok=True)

    stage_times: Dict[str, float] = {}
    query = query_override or build_query(topic)

    stage_start = time.time()
    papers = search_arxiv(query, max_results=max_results)
    stage_times["search"] = round(time.time() - stage_start, 3)
    if not papers:
        print("No papers retrieved", file=sys.stderr)
        return 1

    stage_start = time.time()
    ranked = rank_papers(papers, ranking_interests(topic))
    stage_times["ranking"] = round(time.time() - stage_start, 3)

    stage_start = time.time()
    summarize_papers(ranked)
    stage_times["summarization"] = round(time.time() - stage_start, 3)

    metrics = compute_metrics(ranked, top_k, run_started, stage_times, max_results=max_results, run_date=RUN_DATE)
    stage_start = time.time()
    figures = write_visualizations(ranked, figure_dir, metrics, stage_times, top_k, RUN_DATE)
    stage_times["visualization"] = round(time.time() - stage_start, 3)
    metrics = compute_metrics(ranked, top_k, run_started, stage_times, max_results=max_results, run_date=RUN_DATE)
    metrics["figure_generation_success_rate"] = mean([1.0 if (output / fig["path"]).exists() else 0.0 for fig in figures])
    metrics.update({f"{key}_quality_score": value for key, value in metric_groups(metrics).items()})
    groups = metric_groups(metrics)
    weights = {
        "retrieval": 0.14,
        "ranking": 0.20,
        "freshness": 0.12,
        "diversity": 0.10,
        "summary": 0.16,
        "integrity": 0.12,
        "visualization": 0.08,
        "runtime": 0.08,
    }
    metrics["overall_quality_score"] = round(sum(groups[key] * weights[key] for key in weights), 4)
    figures = write_visualizations(ranked, figure_dir, metrics, stage_times, top_k, RUN_DATE)

    stage_start = time.time()
    snapshot = {
        "run_date": RUN_DATE,
        "topic": topic,
        "query": query,
        "top_k": top_k,
        "metrics": metrics,
        "stage_times": stage_times,
        "figures": figures,
        "warnings": warnings,
        "papers": [asdict(paper) for paper in ranked],
    }
    write_json(output / f"daily-arxiv-briefing-{RUN_DATE}.json", snapshot)
    write_csv(output / f"daily-arxiv-briefing-{RUN_DATE}.csv", ranked, top_k)
    write_markdown(output / f"daily-arxiv-briefing-{RUN_DATE}.md", topic, query, ranked, figures, metrics, warnings, top_k)
    manifest = {
        "outputs": {
            "markdown": f"daily-arxiv-briefing-{RUN_DATE}.md",
            "csv": f"daily-arxiv-briefing-{RUN_DATE}.csv",
            "json": f"daily-arxiv-briefing-{RUN_DATE}.json",
        },
        "row_count": min(top_k, len(ranked)),
        "embedded_figure_count": len(figures),
        "embedded_figure_path_validity_rate": metrics["figure_generation_success_rate"],
        "metric_completeness_rate": 1.0,
        "warnings": warnings,
    }
    write_json(output / f"briefing-manifest-{RUN_DATE}.json", manifest)
    stage_times["briefing_generation"] = round(time.time() - stage_start, 3)

    print(json.dumps({"output_dir": str(output), "retrieved_count": len(ranked), "top_paper": ranked[0].title}, ensure_ascii=False))
    return 0


def refresh_output(output: Path) -> int:
    json_files = sorted(output.glob("daily-arxiv-briefing-*.json"))
    if not json_files:
        print(f"No briefing JSON found in {output}", file=sys.stderr)
        return 1
    snapshot_path = json_files[-1]
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    run_date = snapshot.get("run_date") or RUN_DATE
    topic = snapshot.get("topic") or snapshot.get("topic_raw") or output.name
    query = snapshot.get("query") or ""
    papers = [paper_from_dict(item) for item in snapshot.get("papers", [])]
    if not papers:
        print(f"No papers found in {snapshot_path}", file=sys.stderr)
        return 1

    top_k = int(snapshot.get("top_k") or min(12, len(papers)))
    papers = rank_papers(papers, ranking_interests(topic))
    summarize_papers(papers)
    stage_times = snapshot.get("stage_times") or {
        "search": 0.0,
        "ranking": 0.0,
        "summarization": 0.0,
        "visualization": 0.0,
        "briefing_generation": 0.0,
    }
    max_results = int(max(snapshot.get("metrics", {}).get("retrieved_count", len(papers)), len(papers)))
    figure_dir = output / "figures"
    run_started = time.time() - float(snapshot.get("metrics", {}).get("runtime_seconds", 0.0))
    metrics = compute_metrics(papers, top_k, run_started, stage_times, max_results=max_results, run_date=run_date)
    figures = write_visualizations(papers, figure_dir, metrics, stage_times, top_k, run_date)
    metrics["figure_generation_success_rate"] = mean([1.0 if (output / fig["path"]).exists() else 0.0 for fig in figures])
    metrics.update({f"{key}_quality_score": value for key, value in metric_groups(metrics).items()})
    groups = metric_groups(metrics)
    weights = {
        "retrieval": 0.14,
        "ranking": 0.20,
        "freshness": 0.12,
        "diversity": 0.10,
        "summary": 0.16,
        "integrity": 0.12,
        "visualization": 0.08,
        "runtime": 0.08,
    }
    metrics["overall_quality_score"] = round(sum(groups[key] * weights[key] for key in weights), 4)
    figures = write_visualizations(papers, figure_dir, metrics, stage_times, top_k, run_date)

    snapshot.update(
        {
            "run_date": run_date,
            "topic": topic,
            "query": query,
            "top_k": top_k,
            "metrics": metrics,
            "stage_times": stage_times,
            "figures": figures,
            "papers": [asdict(paper) for paper in papers],
        }
    )
    write_json(output / f"daily-arxiv-briefing-{run_date}.json", snapshot)
    write_csv(output / f"daily-arxiv-briefing-{run_date}.csv", papers, top_k)

    original_run_date = globals()["RUN_DATE"]
    try:
        globals()["RUN_DATE"] = run_date
        write_markdown(output / f"daily-arxiv-briefing-{run_date}.md", topic, query, papers, figures, metrics, snapshot.get("warnings", []), top_k)
    finally:
        globals()["RUN_DATE"] = original_run_date

    manifest = {
        "outputs": {
            "markdown": f"daily-arxiv-briefing-{run_date}.md",
            "csv": f"daily-arxiv-briefing-{run_date}.csv",
            "json": f"daily-arxiv-briefing-{run_date}.json",
        },
        "row_count": min(top_k, len(papers)),
        "embedded_figure_count": len(figures),
        "embedded_figure_path_validity_rate": metrics["figure_generation_success_rate"],
        "metric_completeness_rate": 1.0,
        "overall_quality_score": metrics["overall_quality_score"],
        "warnings": snapshot.get("warnings", []),
    }
    write_json(output / f"briefing-manifest-{run_date}.json", manifest)
    print(json.dumps({"refreshed": str(output), "figures": len(figures), "overall_quality_score": metrics["overall_quality_score"]}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the arXiv briefing skill workflow test.")
    parser.add_argument("--topic", default="recent papers of AI for Finance")
    parser.add_argument("--max-results", type=int, default=30)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--query", default=None, help="Optional explicit arXiv API search_query.")
    parser.add_argument("--refresh-output", default=None, help="Regenerate metrics and figures from an existing output directory.")
    args = parser.parse_args()
    if args.refresh_output:
        return refresh_output(Path(args.refresh_output))
    return run(args.topic, args.max_results, args.top_k, args.query)


if __name__ == "__main__":
    raise SystemExit(main())
