"""
make_15_commits.py — Stage files into 15 logical commits and push to GitHub.
"""
import subprocess
import sys

COMMITS = [
    # 1. gitignore
    {
        "msg": "chore: update repository .gitignore and safety configuration",
        "files": [".gitignore"]
    },
    # 2. backend config & models
    {
        "msg": "feat(backend): add core FastAPI settings, models, and configuration",
        "files": [
            "src/pyproject.toml",
            "src/requirements.txt",
            "src/.env.example",
            "src/backend/__init__.py",
            "src/backend/config.py",
            "src/backend/models.py"
        ]
    },
    # 3. document parser
    {
        "msg": "feat(parser): add PyMuPDF and Markdown document section parser",
        "files": ["src/backend/document_parser.py"]
    },
    # 4. vector store
    {
        "msg": "feat(vectorstore): add ChromaDB vector store initialization and persistence",
        "files": ["src/backend/vector_store.py"]
    },
    # 5. embeddings
    {
        "msg": "feat(embeddings): add provider-independent embeddings layer supporting Gemini and watsonx",
        "files": ["src/backend/embeddings.py"]
    },
    # 6. rag engine
    {
        "msg": "feat(rag): implement grounded RAG engine with prompt-injection defense and thresholding",
        "files": ["src/backend/rag_engine.py"]
    },
    # 7. main API routes
    {
        "msg": "feat(api): add FastAPI REST API routes for health, search, documents, and categories",
        "files": ["src/backend/main.py"]
    },
    # 8. MCP server
    {
        "msg": "feat(mcp): add IBM Bob Model Context Protocol (MCP) STDIO server",
        "files": ["src/mcp_server"]
    },
    # 9. demo data & scripts
    {
        "msg": "feat(data): add synthetic chip design demo documents and seed scripts",
        "files": ["src/demo_data", "src/scripts", "scripts"]
    },
    # 10. test suite
    {
        "msg": "test(backend): add pytest unit and integration test suite",
        "files": ["src/tests"]
    },
    # 11. frontend
    {
        "msg": "feat(frontend): add React 18 SPA frontend application and static assets",
        "files": ["src/frontend", "src/backend/static"]
    },
    # 12. documentation
    {
        "msg": "docs: add comprehensive problem statement, solution overview, architecture, and setup guide",
        "files": [
            "docs/problem-statement.md",
            "docs/solution-overview.md",
            "docs/architecture.md",
            "docs/setup-guide.md",
            "src/README.md"
        ]
    },
    # 13. demo scripts & checklists
    {
        "msg": "docs(demo): add demo recording script, checklist, and video/live URL status",
        "files": [
            "demo/demo-script.md",
            "demo/recording-checklist.md",
            "demo/demo-video-link.txt",
            "demo/live-demo-url.txt"
        ]
    },
    # 14. presentation & screenshots
    {
        "msg": "docs(presentation): add hackathon slide deck, content markdown, speaker notes, and screenshots",
        "files": [
            "presentation",
            "demo/screenshots"
        ]
    },
    # 15. submission metadata & root README
    {
        "msg": "docs(submission): update submission.yaml metadata and root README for hackathon judges",
        "files": [
            "submission.yaml",
            "README.md"
        ]
    }
]

def run(cmd):
    print(f"--> Execution: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.returncode != 0:
        print(f"ERROR ({res.returncode}): {res.stderr.strip()}")
        sys.exit(res.returncode)

def main():
    for idx, c in enumerate(COMMITS, start=1):
        print(f"\n=================== COMMIT {idx}/15 ===================")
        for f in c["files"]:
            run(f"git add \"{f}\"")
        run(f"git commit -m \"{c['msg']}\"")
    
    print("\n=================== PUSHING TO GITHUB ===================")
    run("git push origin main")
    print("\n🎉 SUCCESS: Created 15 commits and pushed all 15 commits to GitHub!")

if __name__ == "__main__":
    main()
