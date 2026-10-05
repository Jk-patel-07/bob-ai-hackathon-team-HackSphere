# Problem Statement — Chip Design Knowledge Assistant

## Background

In semiconductor IC (Integrated Circuit) design, engineering teams rely heavily on Process Design Kits (PDKs), Design Rule Checking (DRC) specifications, Layout Versus Schematic (LVS) guidelines, latchup prevention rules, and timing constraint manuals.

These documents contain hundreds of precise rules, numerical spacing constraints, layer definitions, and layout recommendations provided by semiconductor foundries and internal CAD groups.

## The Problem

Physical design and layout engineers face two primary operational challenges:

1. **Information Fragmentation & Context Switching:** Specifications are stored across multi-page PDF documents, internal wiki pages, and Markdown files. Locating a specific rule (e.g., minimum guard ring spacing or antenna ratio rules) requires switching between layout tools (like Cadence Virtuoso or Synopsys Klayout) and PDF viewers, leading to lost engineering time.
2. **Risk of LLM Hallucinations:** General-purpose AI tools trained on web data frequently produce plausible-sounding but inaccurate answers when queried about precise numerical engineering limits. In semiconductor manufacturing, an incorrect metal width or spacing rule applied during layout can lead to DRC violations or silicon failure.

## Who is Affected

- **Physical Design Engineers:** Engineers creating silicon block layouts who must verify layer rules and clearances against PDK standards.
- **Layout Designers:** Layout specialists needing quick reference to standard cell pitch, well taps, and latchup rules.
- **EDA / CAD Engineers:** Tool flow maintainers who support design teams with script constraints and tech file configurations.

## Why It Matters

Missed or misread design rules lead to iteration loops during DRC clean-up, delaying schedule milestones. Access to verified, grounded documentation directly within the engineering workflow reduces lookup friction and helps prevent human oversight.

## Why Existing Solutions Fall Short

- **Standard Document Search:** Basic keyword search (Ctrl+F in PDFs) requires exact terminology matching and often fails to retrieve relevant context split across tables, diagrams, or separate sections.
- **Generic LLMs:** Standard ungrounded LLMs lack knowledge of proprietary or project-specific PDK documents and risk hallucinating numbers, specs, or rule names.

The **Chip Design Knowledge Assistant** solves these gaps by pairing a dedicated vector retrieval engine with IBM watsonx.ai, designed to minimize hallucinations by grounding answers in retrieved documents and returning an explicit insufficient-information response when supporting evidence is unavailable.
