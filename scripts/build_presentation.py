"""
build_presentation.py — Generate presentation/slides.pptx using python-pptx.
Creates an 8-slide, 16:9 widescreen presentation with enterprise styling,
embedded screenshots, and speaker notes.
"""
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    NAVY = RGBColor(15, 23, 42)      # #0F172A
    BLUE = RGBColor(15, 98, 254)     # #0F62FE (IBM Blue)
    SLATE = RGBColor(71, 85, 105)    # #475569
    LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
    CARD_BG = RGBColor(241, 245, 249)  # #F1F5F9
    BORDER_COL = RGBColor(203, 213, 225) # #CBD5E1

    blank_layout = prs.slide_layouts[6] # Blank slide layout

    # Helper: Set background color
    def set_bg(slide, color=LIGHT_BG):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background() # No border
        return bg

    # Helper: Add header banner
    def add_header(slide, title_text, category_text="CHIP DESIGN KNOWLEDGE ASSISTANT | IBM BOB HACKATHON"):
        # Top accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = BLUE
        line.line.fill.background()

        # Category Tracker
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.733), Inches(0.3))
        tf = cat_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = BLUE

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.9), Inches(11.733), Inches(0.6))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(26)
        p_t.font.bold = True
        p_t.font.color.rgb = NAVY

    # Helper: Add Speaker Notes
    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ── SLIDE 1: Title Slide ────────────────────────────────────────────────
    slide1 = prs.slides.add_slide(blank_layout)
    set_bg(slide1, LIGHT_BG)

    # Accent Card
    card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(10.933), Inches(5.1))
    card.fill.solid()
    card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    card.line.color.rgb = BORDER_COL

    # Title text
    tb = slide1.shapes.add_textbox(Inches(1.8), Inches(1.8), Inches(9.733), Inches(2.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "IBM BOB HACKATHON  •  TRACK: AI"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = BLUE

    p1 = tf.add_paragraph()
    p1.text = "Chip Design Knowledge Assistant"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = NAVY
    p1.space_before = Pt(12)

    p2 = tf.add_paragraph()
    p2.text = "Grounded AI Assistance for Semiconductor Design Rules & Verification Specs"
    p2.font.size = Pt(18)
    p2.font.color.rgb = SLATE
    p2.space_before = Pt(12)

    # Footer Metadata Box
    fb = slide1.shapes.add_textbox(Inches(1.8), Inches(4.5), Inches(9.733), Inches(1.2))
    tf_f = fb.text_frame
    pf1 = tf_f.paragraphs[0]
    pf1.text = "Team Name: TODO: Enter Team Name  |  Technology: watsonx.ai + IBM Bob (MCP) + ChromaDB"
    pf1.font.size = Pt(13)
    pf1.font.bold = True
    pf1.font.color.rgb = NAVY

    add_notes(slide1, "Good day judges. Today we present the Chip Design Knowledge Assistant, built for the IBM Bob Hackathon under the AI Track. Semiconductor design requires managing thousands of precise physical design rules. Our project brings grounded AI intelligence into the engineer's workflow to make spec discovery fast, accurate, and fully traceable.")

    # ── SLIDE 2: Problem ───────────────────────────────────────────────────
    slide2 = prs.slides.add_slide(blank_layout)
    set_bg(slide2)
    add_header(slide2, "The Problem — Information Fragmentation in Chip Design")

    # 3 Column Problem Cards
    card_data = [
        ("Fragmented Knowledge", "PDK rules, DRC decks, latchup specs, and timing guidelines are spread across multi-page PDFs, wikis, and Markdown files."),
        ("Workflow Friction", "Physical design engineers constantly switch context between EDA layout tools and documentation viewers to locate specific rule tolerances."),
        ("Hallucination Risk", "Generic ungrounded AI models frequently hallucinate numeric values—a major risk when verifying nanometer design tolerances.")
    ]

    for i, (title, desc) in enumerate(card_data):
        left = Inches(0.8 + i * 3.98)
        c = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), Inches(3.78), Inches(4.8))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(255, 255, 255)
        c.line.color.rgb = BORDER_COL

        tb = slide2.shapes.add_textbox(left + Inches(0.3), Inches(2.1), Inches(3.18), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = NAVY

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(14)
        p2.font.color.rgb = SLATE
        p2.space_before = Pt(14)

    add_notes(slide2, "Physical design and layout engineers face a major documentation challenge. PDK rules, DRC decks, and latchup specs are scattered across multi-page manuals. Engineers spend significant time searching through PDFs, causing context switching. Senior leads are interrupted for routine lookups, while using general ungrounded AI models carries the dangerous risk of hallucinated numeric tolerances.")

    # ── SLIDE 3: Solution ──────────────────────────────────────────────────
    slide3 = prs.slides.add_slide(blank_layout)
    set_bg(slide3)
    add_header(slide3, "The Solution — Grounded Chip Design Assistant")

    # Left Summary Card
    left_card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    left_card.fill.solid()
    left_card.fill.fore_color.rgb = RGBColor(255, 255, 255)
    left_card.line.color.rgb = BORDER_COL

    tb_l = slide3.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.0), Inches(4.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    pl1 = tf_l.paragraphs[0]
    pl1.text = "Grounded RAG Intelligence"
    pl1.font.size = Pt(20)
    pl1.font.bold = True
    pl1.font.color.rgb = NAVY

    pl2 = tf_l.add_paragraph()
    pl2.text = "Engineers ask natural-language questions and receive answers strictly grounded in indexed semiconductor documentation."
    pl2.font.size = Pt(14)
    pl2.font.color.rgb = SLATE
    pl2.space_before = Pt(12)

    # Right Feature List
    features = [
        ("Semantic Vector Search", "Indexes PDF, Markdown, and TXT specs into ChromaDB vector storage."),
        ("Source Document Citations", "Attaches exact document titles, sections, and similarity scores to answers."),
        ("Anti-Hallucination Safeguards", "Low-confidence thresholding (0.30) returns an explicit fallback message when evidence is missing."),
        ("IBM Bob MCP Server", "Native Model Context Protocol integration for in-IDE querying directly within IBM Bob.")
    ]

    for i, (title, desc) in enumerate(features):
        top = Inches(1.8 + i * 1.2)
        c = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), top, Inches(5.933), Inches(1.05))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(255, 255, 255)
        c.line.color.rgb = BORDER_COL

        tb = slide3.shapes.add_textbox(Inches(6.8), top + Inches(0.12), Inches(5.533), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = BLUE

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = SLATE

    add_notes(slide3, "Our solution is a domain-specific retrieval-augmented generation platform. Engineers query design specs in natural language and receive answers grounded in indexed documents. Crucially, the system includes source citations down to document sections, and enforces an anti-hallucination threshold—if no supporting context is found, it explicitly refuses to guess.")

    # ── SLIDE 4: Architecture ──────────────────────────────────────────────
    slide4 = prs.slides.add_slide(blank_layout)
    set_bg(slide4)
    add_header(slide4, "System Architecture — Decoupled Dual-Interface RAG")

    # Architecture Box Diagram
    arch_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    arch_box.fill.solid()
    arch_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
    arch_box.line.color.rgb = BORDER_COL

    tb_a = slide4.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.933), Inches(4.2))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True

    pa1 = tf_a.paragraphs[0]
    pa1.text = "Decoupled Architecture Flow:"
    pa1.font.size = Pt(18)
    pa1.font.bold = True
    pa1.font.color.rgb = NAVY

    arch_text = """
    1. Client Layer:  React 18 SPA (Web UI)  AND  IBM Bob IDE (via STDIO MCP Transport)
    2. Server Layer:  FastAPI Backend Core (/health, /search, /documents, /categories)
    3. RAG Engine:   PyMuPDF Document Parser + LangChain Heading Splitter + Thresholding (0.30)
    4. Vector Store: ChromaDB Persistent Storage (103 Chunks Indexed)
    5. IBM Cloud AI: watsonx.ai Slate 125m (Embeddings) + Granite 13b Instruct v2 (LLM Generation)
    """
    pa2 = tf_a.add_paragraph()
    pa2.text = arch_text
    pa2.font.size = Pt(14)
    pa2.font.color.rgb = SLATE
    pa2.space_before = Pt(14)

    add_notes(slide4, "Architecturally, a single FastAPI backend core powers both our React Web UI and our IBM Bob MCP server. Ingested PDFs and Markdown files are chunked with PyMuPDF and embedded using watsonx.ai Slate embeddings into ChromaDB. During queries, ChromaDB retrieves top matching chunks, applies similarity thresholding, and passes verified context to the watsonx.ai Granite 13B model for grounded synthesis.")

    # ── SLIDE 5: IBM Bob Integration ───────────────────────────────────────
    slide5 = prs.slides.add_slide(blank_layout)
    set_bg(slide5)
    add_header(slide5, "Load-Bearing IBM Bob Model Context Protocol (MCP) Integration")

    # Left Protocol Card
    left_c = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    left_c.fill.solid()
    left_c.fill.fore_color.rgb = RGBColor(255, 255, 255)
    left_c.line.color.rgb = BORDER_COL

    tb_b = slide5.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.0), Inches(4.2))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True

    pb1 = tf_b.paragraphs[0]
    pb1.text = "In-IDE Knowledge Access"
    pb1.font.size = Pt(20)
    pb1.font.bold = True
    pb1.font.color.rgb = NAVY

    pb2 = tf_b.add_paragraph()
    pb2.text = "IBM Bob acts as the engineer-facing orchestration layer, connecting directly to our FastAPI backend using standard Model Context Protocol (MCP) STDIO tools."
    pb2.font.size = Pt(14)
    pb2.font.color.rgb = SLATE
    pb2.space_before = Pt(12)

    # Right Tool Cards
    tools = [
        ("search_knowledge_base", "Executes top-k vector search in ChromaDB, applies thresholding, and runs watsonx.ai grounded generation."),
        ("get_document_sections", "Retrieves table of contents and section headings for specific indexed specification documents."),
        ("list_ingested_documents", "Lists all indexed documents, category metadata, and active chunk counts."),
        ("check_backend_status", "Verifies FastAPI health status, ChromaDB liveness, and model configuration.")
    ]

    for i, (name, desc) in enumerate(tools):
        top = Inches(1.8 + i * 1.2)
        c = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), top, Inches(5.933), Inches(1.05))
        c.fill.solid()
        c.fill.fore_color.rgb = RGBColor(255, 255, 255)
        c.line.color.rgb = BORDER_COL

        tb = slide5.shapes.add_textbox(Inches(6.8), top + Inches(0.12), Inches(5.533), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f"Tool: {name}"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = BLUE

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = SLATE

    add_notes(slide5, "The IBM Bob Model Context Protocol integration is load-bearing. Instead of leaving the editor to open a browser, engineers query design specs directly inside IBM Bob. Bob recognizes the intent and calls our custom MCP tools—such as search_knowledge_base and get_document_sections—delivering grounded answers and citations straight into the coding workflow.")

    # ── SLIDE 6: Working Demo ──────────────────────────────────────────────
    slide6 = prs.slides.add_slide(blank_layout)
    set_bg(slide6)
    add_header(slide6, "Working Product Verification — Interface Screenshots")

    # Embed 4 screenshots in a 2x2 grid
    target_dir = "demo/screenshots/"
    imgs = [
        ("01-home-dashboard.png", "Assistant Home View (Healthy Backend Status)", Inches(0.8), Inches(1.8)),
        ("02-grounded-query.png", "Grounded Query & Document Citation Result", Inches(6.8), Inches(1.8)),
        ("03-citation-result.png", "Anti-Hallucination Fallback Safeguard", Inches(0.8), Inches(4.5)),
        ("04-knowledge-base.png", "Knowledge Base Overview & Metrics", Inches(6.8), Inches(4.5))
    ]

    for fname, caption, left, top in imgs:
        path = os.path.join(target_dir, fname)
        if os.path.exists(path):
            slide6.shapes.add_picture(path, left, top, width=Inches(5.733), height=Inches(2.3))

            # Caption box
            c_box = slide6.shapes.add_textbox(left, top + Inches(2.32), Inches(5.733), Inches(0.3))
            p = c_box.text_frame.paragraphs[0]
            p.text = caption
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = NAVY

    add_notes(slide6, "Here we see the working application in action. Screenshot 1 displays our Assistant dashboard with green backend liveness status. Screenshot 2 shows a grounded answer for a poly gate overhang query with its source citation. Screenshot 3 demonstrates our anti-hallucination safeguard in action on an unindexed query, and Screenshot 4 shows our Knowledge Base and Document management interface.")

    # ── SLIDE 7: Why It Is Different ───────────────────────────────────────
    slide7 = prs.slides.add_slide(blank_layout)
    set_bg(slide7)
    add_header(slide7, "Key Differentiation — Grounded Rigor vs Generic AI")

    # Table comparing Generic AI vs Chip Design Assistant
    rows, cols = 6, 3
    table_shape = slide7.shapes.add_table(rows, cols, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
    table = table_shape.table

    table.columns[0].width = Inches(3.0)
    table.columns[1].width = Inches(4.366)
    table.columns[2].width = Inches(4.366)

    headers = ["Dimension", "Generic AI Chatbot", "Chip Design Knowledge Assistant"]
    for col_idx, text in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.text = text
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        p = cell.text_frame.paragraphs[0]
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.size = Pt(13)

    data = [
        ("Knowledge Source", "Broad web pre-training memory", "Approved local PDK & spec documents"),
        ("Numeric Accuracy", "May invent plausible tolerances", "Answers constrained strictly to retrieved context"),
        ("Source Traceability", "None or generic web links", "Section-level document citations"),
        ("Missing Knowledge", "Guesses or hallucinates values", "Returns explicit low-confidence fallback response"),
        ("Developer Workflow", "External browser tab context switch", "Embedded in IDE via IBM Bob MCP integration")
    ]

    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if row_idx % 2 == 0 else CARD_BG
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(12)
            p.font.color.rgb = NAVY if col_idx != 2 else BLUE
            if col_idx == 2:
                p.font.bold = True

    add_notes(slide7, "Unlike generic AI chatbots that answer from unverified model memory and risk hallucinating numbers, the Chip Design Knowledge Assistant searches approved documents first. Answers are strictly grounded, fully cited, and backed by automated fallback protection when information is missing—all delivered natively inside IBM Bob via MCP.")

    # ── SLIDE 8: Impact & Next Steps ───────────────────────────────────────
    slide8 = prs.slides.add_slide(blank_layout)
    set_bg(slide8)
    add_header(slide8, "Impact & Future Roadmap")

    # Left Impact Card
    c_imp = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8))
    c_imp.fill.solid()
    c_imp.fill.fore_color.rgb = RGBColor(255, 255, 255)
    c_imp.line.color.rgb = BORDER_COL

    tb_i = slide8.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.0), Inches(4.2))
    tf_i = tb_i.text_frame
    tf_i.word_wrap = True

    pi1 = tf_i.paragraphs[0]
    pi1.text = "Qualitative Value Delivered"
    pi1.font.size = Pt(20)
    pi1.font.bold = True
    pi1.font.color.rgb = NAVY

    imp_text = """
    • Faster Discovery: Eliminates manual PDF searching for physical design rules and DRC tolerances.
    
    • Reduced Interruption: Reduces routine reference questions directed at senior layout leads.
    
    • Verifiable Auditability: Attaches section-level document metadata to every answer for peer verification.
    """
    pi2 = tf_i.add_paragraph()
    pi2.text = imp_text
    pi2.font.size = Pt(13)
    pi2.font.color.rgb = SLATE
    pi2.space_before = Pt(12)

    # Right Future Roadmap Card
    c_fut = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), Inches(1.8), Inches(5.933), Inches(4.8))
    c_fut.fill.solid()
    c_fut.fill.fore_color.rgb = RGBColor(255, 255, 255)
    c_fut.line.color.rgb = BORDER_COL

    tb_f = slide8.shapes.add_textbox(Inches(6.9), Inches(2.1), Inches(5.333), Inches(4.2))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True

    pf1 = tf_f.paragraphs[0]
    pf1.text = "Future Roadmap (Planned Extensions)"
    pf1.font.size = Pt(20)
    pf1.font.bold = True
    pf1.font.color.rgb = BLUE

    fut_text = """
    • Enterprise PDK Connectors: Connectors for proprietary foundry rulebooks & internal CAD wikis.
    
    • Access Control & RBAC: Multi-tenant role-based security for proprietary design projects.
    
    • Version-Aware Knowledge: Process node tagging to distinguish 7nm vs 5nm rule decks.
    """
    pf2 = tf_f.add_paragraph()
    pf2.text = fut_text
    pf2.font.size = Pt(13)
    pf2.font.color.rgb = SLATE
    pf2.space_before = Pt(12)

    add_notes(slide8, "In terms of qualitative impact, this system reduces lookup friction, minimizes senior engineer interruptions, and provides verifiable document auditability. For future work, we plan to add enterprise PDK connectors, role-based access control, and version-aware process node indexing. Thank you!")

    # Save Presentation
    os.makedirs("presentation", exist_ok=True)
    out_path = "presentation/slides.pptx"
    prs.save(out_path)
    print(f"Presentation generated successfully: {out_path}")

if __name__ == "__main__":
    create_deck()
