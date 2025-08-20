# tauri_backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import os
import sqlite3
from pathlib import Path
from typing import Optional

# 🐝 Qween Bee's Fix: Force litellm to accept Ollama models
import litellm
from functools import wraps

# Store original function
_original_get_llm_provider = litellm.get_llm_provider

# Patch it
@wraps(_original_get_llm_provider)
def patched_get_llm_provider(model: str, *args, **kwargs):
    # If it's a known Ollama model, force provider to 'ollama'
    if any(name in model for name in ["phi3", "llama3", "mistral", "gemma"]):
        return "ollama", model, "ollama"
    # Otherwise, use original logic
    return _original_get_llm_provider(model, *args, **kwargs)

# Apply the patch
litellm.get_llm_provider = patched_get_llm_provider

app = FastAPI()

# Resolve repo root and outputs dir robustly (independent of CWD)
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = REPO_ROOT / "outputs"
BLOG_PATH = OUTPUTS_DIR / "blog.md"
LINKEDIN_PATH = OUTPUTS_DIR / "linkedin_post.md"
MEMORY_DB_PATH = OUTPUTS_DIR / "memory.db"

# Allow Tauri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost", "https://tauri.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TopicRequest(BaseModel):
    topic: str

# --------------------
# SQLite helpers
# --------------------

def ensure_outputs_dir():
    try:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"⚠️ Failed creating outputs dir {OUTPUTS_DIR}: {e}")


def get_db() -> sqlite3.Connection:
    ensure_outputs_dir()
    conn = sqlite3.connect(MEMORY_DB_PATH, check_same_thread=False)
    # Improve concurrency and reliability
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
    except Exception as e:
        print(f"⚠️ Failed to set DB pragmas: {e}")
    return conn


def init_db():
    ensure_outputs_dir()
    conn = get_db()
    cur = conn.cursor()

    # Base table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            type TEXT CHECK(type IN ('blog','linkedin')),
            topic TEXT,
            title TEXT,
            content TEXT
        )
        """
    )

    # FTS5 virtual table
    cur.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
            title, content, topic, content='posts', content_rowid='id'
        )
        """
    )

    # Triggers to keep FTS in sync
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS after_posts_insert
        AFTER INSERT ON posts BEGIN
            INSERT INTO posts_fts(rowid, title, content, topic)
            VALUES (new.id, new.title, new.content, new.topic);
        END;
        """
    )
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS after_posts_update
        AFTER UPDATE ON posts BEGIN
            INSERT INTO posts_fts(posts_fts, rowid, title, content, topic)
            VALUES ('delete', old.id, old.title, old.content, old.topic);
            INSERT INTO posts_fts(rowid, title, content, topic)
            VALUES (new.id, new.title, new.content, new.topic);
        END;
        """
    )
    cur.execute(
        """
        CREATE TRIGGER IF NOT EXISTS after_posts_delete
        AFTER DELETE ON posts BEGIN
            INSERT INTO posts_fts(posts_fts, rowid, title, content, topic)
            VALUES ('delete', old.id, old.title, old.content, old.topic);
        END;
        """
    )

    conn.commit()
    conn.close()
    print(f"✅ Memory DB initialized at {MEMORY_DB_PATH}")


@app.on_event("startup")
def on_startup():
    init_db()


# --------------------
# Utility: insert posts
# --------------------

def insert_post(post_type: str, topic: str, title: str, content: str):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO posts (type, topic, title, content)
            VALUES (?, ?, ?, ?)
            """,
            (post_type, topic, title, content),
        )
        conn.commit()
    except Exception as e:
        print(f"⚠️ Failed inserting post into memory: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def extract_blog_title(content: str, fallback: str) -> str:
    try:
        for line in content.splitlines():
            stripped = line.strip().lstrip("\ufeff")  # handle BOM
            if stripped.startswith("# "):
                return stripped[2:].strip() or fallback
        # fallback to first non-empty line
        for line in content.splitlines():
            if line.strip():
                return line.strip()[:120]
    except Exception:
        pass
    return fallback


def extract_linkedin_title(content: str, fallback: str) -> str:
    try:
        for line in content.splitlines():
            stripped = line.strip().lstrip("\ufeff")
            if stripped:
                return stripped[:120]
    except Exception:
        pass
    return fallback


# --------------------
# Streaming crew execution
# --------------------

@app.post("/run-crew-stream")
async def run_crew_stream(request: TopicRequest):
    async def stream_output():
        try:
            # ✅ Print for debugging
            print(f"🚀 Running: python simple_crew.py '{request.topic}'")

            # ✅ Run the crew script from the repo root
            process = await asyncio.create_subprocess_exec(
                "python",
                "simple_crew.py",
                request.topic,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(REPO_ROOT),  # run from repo root
            )

            # ✅ Stream stdout line by line
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                decoded_line = line.decode("utf-8", errors="replace")
                print(f"📤 Streaming: {decoded_line.strip()}")  # Debug output
                yield decoded_line

            # ✅ Check for errors
            stderr_output = await process.stderr.read()
            if stderr_output:
                error_msg = stderr_output.decode("utf-8", errors="replace")
                print(f"❌ Error output: {error_msg}")
                yield f"❌ Error: {error_msg}\n"

            # ✅ Wait for process to finish
            return_code = await process.wait()
            print(f"✅ Process finished with return code: {return_code}")

            # ✅ After process completion, persist generated outputs to memory
            try:
                if BLOG_PATH.exists():
                    blog_content = BLOG_PATH.read_text(encoding="utf-8", errors="ignore")
                    blog_title = extract_blog_title(blog_content, fallback=f"Mindful Tech: {request.topic}")
                    insert_post("blog", request.topic, blog_title, blog_content)
                    print("📝 Blog inserted into memory DB")
                else:
                    print(f"ℹ️ Blog file not found at {BLOG_PATH}")

                if LINKEDIN_PATH.exists():
                    li_content = LINKEDIN_PATH.read_text(encoding="utf-8", errors="ignore")
                    li_title = extract_linkedin_title(li_content, fallback=f"LinkedIn: {request.topic}")
                    insert_post("linkedin", request.topic, li_title, li_content)
                    print("📝 LinkedIn post inserted into memory DB")
                else:
                    print(f"ℹ️ LinkedIn file not found at {LINKEDIN_PATH}")
            except Exception as e:
                print(f"⚠️ Failed to save outputs to memory DB: {e}")

        except Exception as e:
            # ✅ Catch and yield friendly error
            error_msg = f"❌ Error: {str(e)}\n"
            print(error_msg)
            yield error_msg

    # ✅ Return streaming response
    return StreamingResponse(stream_output(), media_type="text/plain")


# --------------------
# Health & legacy file-based endpoints (kept for compatibility)
# --------------------

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/latest-blog")
async def get_latest_blog():
    try:
        if BLOG_PATH.exists():
            content = BLOG_PATH.read_text(encoding="utf-8", errors="ignore")
            return {"content": content}
        # Fallback to any older files if needed
        import glob
        files = list(REPO_ROOT.glob("mindful_tech_simple_output_*.md"))
        if not files:
            return {"content": "# No blog found yet\n\nRun the crew to generate one!"}
        latest_file = max(files, key=lambda p: p.stat().st_ctime)
        content = latest_file.read_text(encoding="utf-8", errors="ignore")
        return {"content": content}
    except Exception as e:
        return {"content": f"# Error loading blog\n\n{str(e)}"}


@app.get("/latest-linkedin")
async def get_latest_linkedin():
    try:
        if LINKEDIN_PATH.exists():
            content = LINKEDIN_PATH.read_text(encoding="utf-8", errors="ignore")
            return {"content": content}
        else:
            return {"content": "# No LinkedIn post found yet\n\nRun the crew to generate one!"}
    except Exception as e:
        return {"content": f"# Error loading LinkedIn post\n\n{str(e)}"}


# --------------------
# Memory API
# --------------------

@app.get("/memory/list")
async def list_posts(filter_type: Optional[str] = None, limit: int = 50, offset: int = 0):
    try:
        conn = get_db()
        cur = conn.cursor()
        query = "SELECT id, created_at, type, topic, title FROM posts"
        params: list = []
        if filter_type:
            if filter_type not in ("blog", "linkedin"):
                return {"error": "invalid type"}
            query += " WHERE type = ?"
            params.append(filter_type)
        query += " ORDER BY datetime(created_at) DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cur.execute(query, params)
        rows = cur.fetchall()
        posts = [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "type": row["type"],
                "topic": row["topic"],
                "title": row["title"],
            }
            for row in rows
        ]
        return {"posts": posts}
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/memory/post/{post_id}")
async def get_post(post_id: int):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, created_at, type, topic, title, content
            FROM posts WHERE id = ?
            """,
            (post_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"error": "Post not found"}
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "type": row["type"],
            "topic": row["topic"],
            "title": row["title"],
            "content": row["content"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/memory/latest")
async def get_latest_post(filter_type: Optional[str] = None):
    try:
        conn = get_db()
        cur = conn.cursor()
        query = "SELECT id, created_at, type, topic, title, content FROM posts"
        params: list = []
        if filter_type:
            if filter_type not in ("blog", "linkedin"):
                return {"error": "invalid type"}
            query += " WHERE type = ?"
            params.append(filter_type)
        query += " ORDER BY datetime(created_at) DESC LIMIT 1"
        cur.execute(query, params)
        row = cur.fetchone()
        if not row:
            return {"error": "No posts found"}
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "type": row["type"],
            "topic": row["topic"],
            "title": row["title"],
            "content": row["content"],
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/memory/search")
async def search_posts(q: str, limit: int = 50):
    try:
        conn = get_db()
        cur = conn.cursor()
        # Join FTS to base table to retrieve metadata
        cur.execute(
            """
            SELECT p.id, p.created_at, p.type, p.topic, p.title
            FROM posts_fts f
            JOIN posts p ON p.id = f.rowid
            WHERE f MATCH ?
            ORDER BY datetime(p.created_at) DESC
            LIMIT ?
            """,
            (q, limit),
        )
        rows = cur.fetchall()
        posts = [
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "type": row["type"],
                "topic": row["topic"],
                "title": row["title"],
            }
            for row in rows
        ]
        return {"posts": posts}
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


@app.get("/memory/topics")
async def list_topics():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT topic, COUNT(*) as count
            FROM posts
            WHERE topic IS NOT NULL AND topic != ''
            GROUP BY topic
            ORDER BY count DESC, topic ASC
            """
        )
        rows = cur.fetchall()
        return {
            "topics": [
                {"topic": row["topic"], "count": row["count"]} for row in rows
            ]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass
