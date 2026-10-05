# Speaker Notes — Chip Design Knowledge Assistant

**Target Length:** ~4 Minutes (~25–35 seconds per slide)  
**Tone:** Technical, clear, factual, and confident.

---

### Slide 1: Title (0:00 – 0:25)
*"Good day judges. Today we are presenting the Chip Design Knowledge Assistant, built for the IBM Bob Hackathon under the AI Track. Semiconductor design requires managing thousands of precise physical design rules. Our project brings grounded AI intelligence into the engineer's workflow to make spec discovery fast, accurate, and fully traceable."*

---

### Slide 2: Problem (0:25 – 0:55)
*"Physical design and layout engineers face a major documentation challenge. PDK rules, DRC decks, and latchup specs are scattered across multi-page manuals and wiki pages. Engineers spend significant time searching through PDFs, causing constant context switching. Junior engineers frequently interrupt senior leads for routine lookups, while using general ungrounded AI models carries the dangerous risk of hallucinated numeric tolerances."*

---

### Slide 3: Solution (0:55 – 1:25)
*"Our solution is a domain-specific retrieval-augmented generation platform. Engineers query design specs in natural language and receive answers grounded in indexed documents. Crucially, the system includes source citations down to document sections, and enforces an anti-hallucination threshold—if no supporting context is found, it explicitly refuses to guess."*

---

### Slide 4: Architecture (1:25 – 1:55)
*"Architecturally, a single FastAPI backend core powers both our React Web UI and our IBM Bob MCP server. Ingested PDFs and Markdown files are chunked with PyMuPDF and embedded using watsonx.ai Slate embeddings into ChromaDB. During queries, ChromaDB retrieves top matching chunks, applies similarity thresholding, and passes verified context to the watsonx.ai Granite 13B model for grounded synthesis."*

---

### Slide 5: IBM Bob Integration (1:55 – 2:30)
*"The IBM Bob Model Context Protocol integration is load-bearing. Instead of leaving the editor to open a browser, engineers query design specs directly inside IBM Bob. Bob recognizes the intent and calls our custom MCP tools—such as `search_knowledge_base` and `get_document_sections`—delivering grounded answers and citations straight into the coding workflow."*

---

### Slide 6: Working Demo (2:30 – 3:05)
*"Here we see the working application in action. Screenshot 1 displays our Assistant dashboard with green backend liveness status. Screenshot 2 shows a grounded answer for a poly gate overhang query with its source citation. Screenshot 3 demonstrates our anti-hallucination safeguard in action on an unindexed query, and Screenshot 4 shows our Knowledge Base and Document management interface."*

---

### Slide 7: Why It Is Different (3:05 – 3:35)
*"Unlike generic AI chatbots that answer from unverified model memory and risk hallucinating numbers, the Chip Design Knowledge Assistant searches approved documents first. Answers are strictly grounded, fully cited, and backed by automated fallback protection when information is missing—all delivered natively inside IBM Bob via MCP."*

---

### Slide 8: Impact & Next Steps (3:35 – 4:05)
*"In terms of qualitative impact, this system reduces lookup friction, minimizes senior engineer interruptions, and provides verifiable document auditability. For future work, we plan to add enterprise PDK connectors, role-based access control, and version-aware process node indexing. Thank you!"*
