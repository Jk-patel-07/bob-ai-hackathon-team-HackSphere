# Demo Recording Checklist — Chip Design Knowledge Assistant

Use this checklist before, during, and after recording the demo video for final submission.

---

## 📋 Before Recording

- [ ] **Start Backend Server:** Verify FastAPI backend is running (`python -m uvicorn backend.main:app --port 8000`).
- [ ] **Verify Health Endpoint:** Confirm `http://localhost:8000/health` returns `status: ok` and `total_chunks: 103`.
- [ ] **Seed Demo Data:** Run `python scripts/seed_demo_data.py` to ensure all 5 synthetic documents are indexed.
- [ ] **Configure Display:** Set screen resolution to 1440 × 900 or 1920 × 1080 (16:9 aspect ratio).
- [ ] **Clean Environment:**
  - Close developer tools / browser console.
  - Close unneeded browser tabs and personal messaging windows.
  - Disable OS notifications (Do Not Disturb / Focus Mode).
  - Hide sensitive terminal paths or personal credentials.
- [ ] **Audio Test:** Perform a 10-second test recording to verify microphone volume and clear audio.

---

## 🎬 During Recording

- [ ] **Pacing:** Speak clearly and deliberately at a steady cadence.
- [ ] **Follow Timeline:** Stick to the 4-minute structure in `demo/demo-script.md`.
- [ ] **Highlight Key Features:**
  - Grounded answer generation + section citation (`synthetic_pdk_design_rules.md`).
  - Low-confidence fallback response on unindexed query ("FinFET fin pitch").
  - IBM Bob MCP tool invocation (`search_knowledge_base`).
  - Documents management table & upload interface.
- [ ] **No Editing Tricks:** Ensure all responses shown are generated live by the application.

---

## 🔍 After Recording

- [ ] **Review Video Quality:** Confirm video resolution is 720p minimum (1080p recommended) with crisp text.
- [ ] **Review Audio:** Check that audio is clear without background noise or heavy clipping.
- [ ] **Privacy Audit:** Verify no `WATSONX_API_KEY`, API tokens, or personal emails appear in video frames.
- [ ] **Upload to Host:** Upload to YouTube (Unlisted), Loom, or IBM Box.
- [ ] **Set View Permissions:** Set permissions to *"Anyone with the link can view"* so hackathon judges can access.
- [ ] **Update Link:** Update `demo/demo-video-link.txt` with the final accessible video URL.
