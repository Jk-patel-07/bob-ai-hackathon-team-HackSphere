# Demo Script — Chip Design Knowledge Assistant

**Target Length:** ~4 Minutes  
**Audience:** IBM Bob Hackathon Judges  
**Key Goal:** Demonstrate real working grounded RAG, anti-hallucination safeguards, IBM Bob MCP integration, and document management.

---

## Video Timeline & Presentation Script

### 0:00 – 0:20 | Problem Statement
- **Visual:** Slide or direct view of complex semiconductor design manuals / EDA verification layout.
- **Narrator Script:**  
  *"Physical design and layout engineers spend substantial time looking up complex PDK rules, DRC tolerances, and latchup guidelines scattered across multi-page manuals. Context switching between EDA layout tools and PDFs slows down design verification. Generic AI tools can hallucinate critical numeric tolerances, creating expensive risks if relied upon blindly."*

### 0:20 – 0:40 | Solution Overview
- **Visual:** Switch to **Chip Design Knowledge Assistant** home screen (`01-home-dashboard.png`).
- **Narrator Script:**  
  *"To solve this, we built the Chip Design Knowledge Assistant. It combines IBM watsonx.ai, ChromaDB vector retrieval, FastAPI, and an IBM Bob Model Context Protocol (MCP) server. The assistant is designed to minimize hallucinations by strictly grounding answers in retrieved document context and returning an insufficient-information response when evidence is unavailable."*

### 0:40 – 1:20 | Knowledge Base & Synthetic Data
- **Visual:** Navigate to **Knowledge Base** tab (`04-knowledge-base.png`) and **Documents** tab (`05-documents.png`).
- **Narrator Script:**  
  *"Here in the Knowledge Base view, we can see 5 indexed synthetic document packages containing 103 vectorized text chunks across categories like PDK Rules, DRC Guidelines, and Latchup Specs. Note that all sample files shipped in the repository are synthetic demo documents created for testing, not proprietary foundry rules."*

### 1:20 – 2:10 | Grounded RAG Query & Source Citation
- **Visual:** Navigate to **Assistant** chat screen. Type query: *"What is the minimum poly gate overhang beyond the active region?"* (`02-grounded-query.png`).
- **Narrator Script:**  
  *"Let's submit a grounded engineering query: 'What is the minimum poly gate overhang beyond the active region?' The RAG engine performs vector similarity search in ChromaDB, retrieves the top relevant context chunk, and passes it to IBM watsonx.ai. Notice the exact answer returned along with a clear source citation referencing Section 3.1 of synthetic_pdk_design_rules.md."*

### 2:10 – 2:40 | Anti-Hallucination Safeguard
- **Visual:** Type unindexed query: *"What is the FinFET fin pitch?"* (`03-citation-result.png`).
- **Narrator Script:**  
  *"Now let's test anti-hallucination protection by asking a question not present in our indexed documents: 'What is the FinFET fin pitch?' Instead of fabricating a plausible number, the similarity score falls below our configured threshold of 0.30, and the system cleanly returns an explicit insufficient-information response."*

### 2:40 – 3:25 | IBM Bob MCP Integration
- **Visual:** Switch to IBM Bob IDE window calling `search_knowledge_base` MCP tool.
- **Narrator Script:**  
  *"Developers can also access this knowledge without leaving their IDE. Using the custom Model Context Protocol (MCP) STDIO server, IBM Bob natively invokes the `search_knowledge_base` tool to retrieve grounded chip design rules directly inside code editing sessions."*

### 3:25 – 3:50 | Document Ingestion & Management
- **Visual:** Navigate to **Documents** page (`05-documents.png`) and show upload drop zone.
- **Narrator Script:**  
  *"Adding new specification documents is seamless. Design leads can upload new Markdown, PDF, or TXT files through the Documents tab. The system automatically parses headings, generates embeddings, and indexes the content into vector storage immediately."*

### 3:50 – 4:10 | Conclusion & Impact
- **Visual:** Return to Assistant home screen.
- **Narrator Script:**  
  *"The Chip Design Knowledge Assistant delivers faster, grounded specification lookups, eliminates context switching, and enforces strict safeguards against AI hallucinations. Thank you!"*
