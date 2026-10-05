# Chip Design Knowledge Assistant — Presentation Deck

**Track:** AI  
**Event:** IBM Bob Hackathon  
**Target Length:** 8 Slides (~4 Minutes)  

---

## Slide 1: Title

### Slide Content
- **Title:** Chip Design Knowledge Assistant
- **Subtitle:** Grounded AI assistance for semiconductor design knowledge
- **Track:** AI Track
- **Event:** IBM Bob Hackathon
- **Team Name:** TODO: Enter Team Name

---

## Slide 2: Problem

### Slide Content
- **Header:** The Problem — Information Fragmentation in Chip Design
- **Key Challenge:** Semiconductor engineers navigate hundreds of pages across PDK rules, DRC decks, latchup guidelines, and timing manuals.
- **Pain Points:**
  - **Knowledge Fragmentation:** Technical specs split across multi-page PDFs, wikis, and Markdown files.
  - **Workflow Interruption:** Frequent context switching between EDA layout tools and manuals.
  - **Onboarding Bottlenecks:** Junior engineers repeatedly interrupt senior staff for spec lookups.
  - **Risk of LLM Hallucinations:** Generic ungrounded AI models risk hallucinating numeric design tolerances.

---

## Slide 3: Solution

### Slide Content
- **Header:** The Solution — Grounded Chip Design Knowledge Assistant
- **Core Mechanism:** An intelligent RAG assistant that retrieves approved engineering context before generating answers.
- **Key Capabilities:**
  - **Semantic Retrieval:** Vector search in ChromaDB across indexed design documents.
  - **Source-Grounded Generation:** IBM watsonx.ai Granite LLM synthesizes answers constrained strictly by retrieved text.
  - **Verifiable Citations:** Exact document, section, and page metadata attached to every answer.
  - **Anti-Hallucination Safeguards:** Low-confidence similarity fallback (threshold `0.30`) returns an explicit insufficient-information message when supporting evidence is missing.
  - **IBM Bob MCP Integration:** Direct access within the IDE workspace via Model Context Protocol (MCP) tools.

---

## Slide 4: Architecture

### Slide Content
- **Header:** Architecture — RAG Pipeline & Dual Interface Access

```
[ Engineer / IDE ]                 [ Web Browser ]
         │                                │
         ▼                                ▼
[ IBM Bob Assistant ]             [ React 18 SPA Frontend ]
         │ (STDIO MCP)                    │ (REST API)
         ▼                                ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Backend Server                    │
│   • /health   • /search   • /documents   • /categories  │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                RAG Orchestration Engine                 │
│   • PyMuPDF & LangChain Chunking                        │
│   • ChromaDB Vector Storage & Similarity Thresholding  │
└──────────────┬───────────────────────────┬──────────────┘
               │                           │
               ▼                           ▼
  [ watsonx.ai Slate Embeddings ]   [ watsonx.ai Granite LLM ]
```

- **Clean Decoupling:** Single FastAPI core serves both the React Web UI and the IBM Bob MCP server.

---

## Slide 5: IBM Bob Integration

### Slide Content
- **Header:** Load-Bearing IBM Bob MCP Integration
- **Direct Workspace Workflow:**
  - Engineer asks a technical design rule question inside IBM Bob.
  - Bob identifies the knowledge task and invokes standard Model Context Protocol (MCP) tools.
  - The MCP server queries the RAG engine and retrieves verified section context.
  - watsonx.ai generates a grounded response.
  - Bob displays the answer along with source document citations inline in the editor.
- **Implemented MCP Tools:**
  - `search_knowledge_base`: Executes semantic vector search + RAG generation.
  - `get_document_sections`: Returns section headings for specific documents.
  - `list_ingested_documents`: Lists all indexed knowledge packages and chunk counts.
  - `check_backend_status`: Returns liveness, vector store status, and model configuration.

---

## Slide 6: Working Demo

### Slide Content
- **Header:** Working Product Verification
- **Visual Grid:**
  - **Frame 1 (Assistant Home):** Reactive UI with backend liveness status (`Backend Connected | 103 Chunks`).
  - **Frame 2 (Grounded Query Answer):** Answer to *"What is the minimum poly gate overhang?"* with section citation (`synthetic_pdk_design_rules.md | Section 3.1`).
  - **Frame 3 (Anti-Hallucination Safeguard):** Low-confidence fallback response for unindexed query (*"What is the FinFET fin pitch?"*).
  - **Frame 4 (Knowledge Base & Documents):** Document list table showing 5 synthetic spec files across 5 categories.

---

## Slide 7: Why It Is Different

### Slide Content
- **Header:** Key Differentiation — Grounded Rigor vs Generic AI

| Dimension | Generic AI Chatbot | Chip Design Knowledge Assistant |
|---|---|---|
| **Knowledge Source** | Ungrounded web pre-training | Approved local PDK & spec documents |
| **Numeric Accuracy** | May invent plausible tolerances | Answers constrained strictly to retrieved context |
| **Source Traceability** | None or URL links | Section-level document citations |
| **Missing Knowledge** | Guesses or hallucinates | Returns explicit insufficient-information response |
| **Developer Workflow** | External web tab | Embedded in IDE via IBM Bob MCP integration |

---

## Slide 8: Impact & Next Steps

### Slide Content
- **Header:** Potential Impact & Future Roadmap
- **Qualitative Value:**
  - **Faster Discovery:** Rapid lookup of physical design rules and DRC specifications.
  - **Reduced Interruptions:** Decreases repeated routine reference questions to senior layout leads.
  - **Verifiable Auditability:** Every answer links directly back to exact manual sections.
- **Future Roadmap (Planned Extensions):**
  - Enterprise PDK and CAD wiki document connectors.
  - Role-Based Access Control (RBAC) & multi-tenant user authentication.
  - Version-aware process node knowledge indexing (e.g., 7nm vs 5nm rule decks).
