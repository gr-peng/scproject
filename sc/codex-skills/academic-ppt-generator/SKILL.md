---
name: academic-ppt-generator
description: Generate concise, editable academic PowerPoint presentations from a bundled local PPTX template. Use when Codex needs to create, draft, or refine scholarly presentation decks, research talks, paper summaries, proposal defenses, lab meeting slides, conference talks, or thesis-style PPTX files where all text, shapes, tables, and charts should remain editable rather than flattened into screenshots.
---

# Academic PPT Generator

Create clean academic presentation decks using the local template in `assets/academic-template.pptx`. Keep every slide element editable: use PowerPoint text boxes, shapes, tables, and editable charts; avoid full-slide images except for explicitly supplied figures.

## Quick Start

1. Inspect the user's topic, audience, time limit, and requested slide count.
2. Build a short outline before generating slides.
3. Use `scripts/build_academic_deck.py` when a structured PPTX is needed.
4. Use the template at `assets/academic-template.pptx` unless the user provides a different template.
5. Validate that the output exists and contains editable shapes, not rasterized slide screenshots.

Example:

```bash
python scripts/build_academic_deck.py outline.json output.pptx
```

The script expects `outline.json` with:

```json
{
  "title": "Talk title",
  "subtitle": "Venue or context",
  "authors": "Name, affiliation",
  "slides": [
    {
      "layout": "title",
      "title": "Talk title",
      "subtitle": "One-line thesis"
    },
    {
      "layout": "bullets",
      "title": "Motivation",
      "bullets": ["Problem context", "Gap", "Why it matters"]
    }
  ]
}
```

## Deck Structure

Prefer 8-14 slides for a short academic talk:

1. Title
2. Research question or thesis
3. Motivation and gap
4. Related work or background
5. Method overview
6. Data, setup, or experimental design
7. Key result 1
8. Key result 2
9. Ablation, limitations, or robustness
10. Takeaways
11. Future work
12. Q&A

For paper summaries, use: problem, contribution, method, experiments, findings, limitations, discussion. For project proposals, use: motivation, hypothesis, method, feasibility, timeline, expected contribution.

## Layout Types

Use these slide types in generated outlines:

- `title`: title, subtitle, authors.
- `section`: one large section title plus a short framing sentence.
- `bullets`: title plus 3-5 concise bullets.
- `two_column`: title, left heading/content, right heading/content.
- `method`: title plus numbered editable process boxes.
- `results`: title, key message, editable chart or table, interpretation bullets.
- `table`: title plus editable table rows.
- `takeaways`: 3-4 large takeaway statements.
- `qa`: closing title and contact or project links.

## Academic Design Rules

- Keep slides sparse: one claim per slide, 25-45 words for normal content slides.
- Use a consistent grid, wide margins, and aligned objects.
- Prefer high-contrast dark text on light backgrounds.
- Use restrained accent colors from the template; do not create one-hue decorative gradients.
- Use editable vector shapes for diagrams, pipelines, timelines, and callouts.
- Use editable PowerPoint charts for numeric results when possible.
- Use tables for comparisons, datasets, model variants, or metric summaries.
- Place captions below figures or charts; keep captions short and factual.
- Avoid decorative stock images, excessive icons, and dense paragraphs.
- Never render slide text into bitmap images.

## Editable Output Requirements

Every generated PPTX should satisfy:

- Titles, bullets, captions, labels, and equations-as-text are editable text.
- Boxes, arrows, dividers, and process diagrams are editable shapes.
- Tables are editable PowerPoint tables.
- Charts are editable PowerPoint chart objects when `python-pptx` supports the requested chart.
- External figures are inserted only when the user provides or requests figures; label and caption them with editable text.
- Speaker notes may summarize narration, assumptions, or citations, but should not replace visible slide content.

## Content Standards

- Start with the core research question and why it matters.
- Make each slide title a claim when possible.
- Include enough methodological detail for an academic audience to judge validity.
- Separate findings from interpretation.
- Surface assumptions, limitations, and threats to validity.
- Add citations in compact form, such as `(Author, Year)` or `[1]`, when sources are provided.
- Do not fabricate citations, numbers, or experimental results.

## Quality Checklist

Before finishing:

- Verify the PPTX file was created.
- Check slide count and outline match the user's requested scope.
- Confirm the template file was used or explain why it was unavailable.
- Confirm visible content is editable wherever possible.
- Confirm no slide is overloaded with text.
- Confirm output path is reported with an absolute local path.

## Resources

- `assets/academic-template.pptx`: default local PowerPoint template copied from the user's workspace.
- `scripts/build_academic_deck.py`: creates a PPTX from a structured JSON outline using editable PowerPoint objects.
- `references/academic_ppt_design.md`: compact design and content guidance for scholarly decks.
