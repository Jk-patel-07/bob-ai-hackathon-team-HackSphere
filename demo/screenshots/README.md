# Screenshots — Chip Design Knowledge Assistant

This directory contains real interface screenshots of the running application at a desktop resolution (16:9 aspect ratio).

## Screenshots Inventory

### `01-home-dashboard.png`
**Description:** Application home view showing the Assistant interface, clean dark theme UI, suggested question cards, chat input bar, and the reactive backend status badge (`Backend Connected | 103 Chunks Indexed`).

### `02-grounded-query.png`
**Description:** Grounded RAG query demonstration. Shows a physical design engineer asking: *"What is the minimum poly gate overhang beyond the active region?"* and receiving a grounded answer backed by an explicit section-level citation (`synthetic_pdk_design_rules.md | Section 3.1`).

### `03-citation-result.png`
**Description:** Anti-hallucination and citation thresholding view. Demonstrates asking an unindexed query (*"What is the FinFET fin pitch?"*), showing the explicit low-confidence fallback message (*"I could not find sufficient information..."*) and similarity score notification (`Similarity score fell below threshold 0.30`).

### `04-knowledge-base.png`
**Description:** Knowledge Base overview displaying total indexed documents (5), vector chunk count (103), active categories (5), and category cards (PDK Rules, DRC Guidelines, Latchup Specs, SPICE Models, Timing Constraints).

### `05-documents.png`
**Description:** Document Management table showing indexed synthetic semiconductor files (`synthetic_pdk_design_rules.md`, `synthetic_drc_standard_cells.md`, etc.), chunk counts, file format badges, upload drop zone, and delete actions.
