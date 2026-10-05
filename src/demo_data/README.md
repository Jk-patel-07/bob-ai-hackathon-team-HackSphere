# Demo Knowledge Base — README

This directory contains **synthetic, educational chip design documents** created
specifically for the IBM Bob Hackathon demo.

> ⚠️ **IMPORTANT**: These documents are entirely synthetic and intended only to
> demonstrate the knowledge-base ingestion and retrieval pipeline. They do NOT
> represent real proprietary PDK rules, DRC specifications, or semiconductor
> process data from any actual foundry or company.
>
> Do NOT use these values for real chip design. Always refer to your foundry's
> official PDK documentation.

## Document Index

| File | Category | Description |
|---|---|---|
| `synthetic_pdk_design_rules.md` | PDK | General transistor sizing and layout rules |
| `synthetic_drc_standard_cells.md` | DRC | Design rule check constraints for standard cells |
| `synthetic_latchup_guidelines.md` | Design Guidelines | Latch-up prevention practices |
| `synthetic_spice_model_notes.md` | SPICE Models | SPICE model parameter usage notes |
| `synthetic_timing_constraints.md` | Application Notes | Static timing analysis setup guidelines |

## Using These Documents

Ingest all demo documents at once using the seed script:

```bash
cd src
python scripts/seed_demo_data.py
```

Or ingest individually via the API:

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "demo_data/synthetic_pdk_design_rules.md", "category": "PDK"}'
```
