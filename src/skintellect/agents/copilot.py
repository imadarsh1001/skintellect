"""
Deep Agents Research Copilot harness for conversational skincare formulation analysis.
Provides session memory, task decomposition (TodoList), and grounded plain-language explanations.
Includes SQLite persistence to preserve conversations across server restarts and IDE crashes.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from skintellect.agents.graph import run_research_graph, stream_research_graph
from skintellect.agents.intent import classify_and_plan
from skintellect.catalog.store import get_catalog
from skintellect.database import database
from skintellect.agents.tools import (
    get_ingredient_graph_tool,
    get_product_detail_tool,
    get_review_insights_tool,
    get_scientific_references_tool,
    search_catalog_tool,
)


def ensure_copilot_tables(db_path: Optional[str] = None):
    """Additive schema migration for persistent conversation threads."""
    path = get_catalog(db_path).path
    with database(path) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS copilot_sessions (
            session_id TEXT PRIMARY KEY,
            persona_id TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS copilot_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_copilot_messages_session ON copilot_messages(session_id);
        """)


class ResearchCopilotSession:
    """Manages thread-scoped conversational state, task planning, and memory."""

    def __init__(self, session_id: str, persona_id: str = "uap", title: str = "New Research Session"):
        self.session_id = session_id
        self.persona_id = persona_id
        self.title = title
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.messages: List[Dict[str, Any]] = []
        self.todo_list: List[Dict[str, Any]] = []
        self.pending_clarification: Optional[Dict[str, Any]] = None

    def persist_message(self, role: str, content: str, timestamp: str, db_path: Optional[str] = None):
        """Additive transaction persisting individual messages to SQLite."""
        try:
            path = get_catalog(db_path).path
            ensure_copilot_tables(path)
            with database(path) as c:
                c.execute("""
                    INSERT INTO copilot_sessions (session_id, persona_id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET title=excluded.title, updated_at=excluded.updated_at
                """, (self.session_id, self.persona_id, self.title, self.created_at, self.updated_at))
                c.execute("""
                    INSERT INTO copilot_messages (session_id, role, content, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (self.session_id, role, content, timestamp))
        except Exception:
            pass  # Fall back gracefully to in-memory state

    def plan_task(self, query: str, history: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Decomposes a user research request into structured subtasks based on query intent."""
        plan = classify_and_plan(query, history=history or self.messages)
        self.todo_list = plan.todo_list
        return plan.todo_list

    def ask(
        self,
        query: str,
        product_ids: Optional[List[int]] = None,
        planning_mode: str = "auto",
        db_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a turn of the research copilot, updating conversational context and plan.
        """
        prior_messages = list(self.messages)
        now_iso = datetime.now(timezone.utc).isoformat()
        self.messages.append({"role": "user", "content": query, "timestamp": now_iso})
        self.updated_at = now_iso

        # Set title if first user message
        user_turns = [m for m in self.messages if m.get("role") == "user"]
        if len(user_turns) == 1:
            clean = query.strip()
            self.title = (clean[:36] + "...") if len(clean) > 36 else clean

        self.persist_message("user", query, now_iso, db_path=db_path)

        # Check if user query resolves an active pending clarification
        effective_query = query
        if self.pending_clarification:
            from skintellect.agents.clarification import resolve_shorthand_clarification
            resolved = resolve_shorthand_clarification(
                query,
                self.pending_clarification.get("options", []),
                self.pending_clarification.get("original_query", ""),
            )
            if resolved:
                effective_query = resolved

        self.plan_task(effective_query, history=prior_messages)

        # Delegate execution to the LangGraph deterministic research workflow
        result = run_research_graph(
            question=effective_query,
            product_ids=product_ids,
            persona_id=self.persona_id,
            planning_mode=planning_mode,
            db_path=db_path,
            history=prior_messages,
            pending_clarification=self.pending_clarification,
        )

        if result.get("clarification"):
            self.pending_clarification = dict(result["clarification"])
            self.pending_clarification["original_query"] = effective_query
        else:
            self.pending_clarification = None

        for task in self.todo_list:
            task["status"] = "completed"

        ans_iso = datetime.now(timezone.utc).isoformat()
        ans_content = result.get("answer", "")
        self.messages.append({"role": "assistant", "content": ans_content, "timestamp": ans_iso})
        self.persist_message("assistant", ans_content, ans_iso, db_path=db_path)

        return result | {
            "todo_list": self.todo_list,
            "session_id": self.session_id,
            "session_title": self.title,
        }

    def stream_ask(
        self,
        query: str,
        product_ids: Optional[List[int]] = None,
        planning_mode: str = "auto",
        db_path: Optional[str] = None
    ):
        """
        Executes a turn of the research copilot, yielding live streaming LangGraph events.
        Persists messages and updates session memory at completion.
        """
        prior_messages = list(self.messages)
        now_iso = datetime.now(timezone.utc).isoformat()
        self.messages.append({"role": "user", "content": query, "timestamp": now_iso})
        self.updated_at = now_iso

        user_turns = [m for m in self.messages if m.get("role") == "user"]
        if len(user_turns) == 1:
            clean = query.strip()
            self.title = (clean[:36] + "...") if len(clean) > 36 else clean

        self.persist_message("user", query, now_iso, db_path=db_path)

        # Check if user query resolves an active pending clarification
        effective_query = query
        if self.pending_clarification:
            from skintellect.agents.clarification import resolve_shorthand_clarification
            resolved = resolve_shorthand_clarification(
                query,
                self.pending_clarification.get("options", []),
                self.pending_clarification.get("original_query", ""),
            )
            if resolved:
                effective_query = resolved

        self.plan_task(effective_query, history=prior_messages)

        for event_payload in stream_research_graph(
            question=effective_query,
            product_ids=product_ids,
            persona_id=self.persona_id,
            planning_mode=planning_mode,
            db_path=db_path,
            history=prior_messages,
            pending_clarification=self.pending_clarification,
        ):
            if event_payload.get("event") == "final_result":
                final_result = event_payload.get("data", {})
                if final_result.get("clarification"):
                    self.pending_clarification = dict(final_result["clarification"])
                    self.pending_clarification["original_query"] = effective_query
                else:
                    self.pending_clarification = None

                for task in self.todo_list:
                    task["status"] = "completed"
                ans_iso = datetime.now(timezone.utc).isoformat()
                ans_content = final_result.get("answer", "")
                self.messages.append({"role": "assistant", "content": ans_content, "timestamp": ans_iso})
                self.persist_message("assistant", ans_content, ans_iso, db_path=db_path)

                event_payload["data"]["todo_list"] = self.todo_list
                event_payload["data"]["session_id"] = self.session_id
                event_payload["data"]["session_title"] = self.title

            yield event_payload

    def clear(self, db_path: Optional[str] = None):
        """Clears all conversation messages and plan."""
        self.messages = []
        self.todo_list = []
        self.updated_at = datetime.now(timezone.utc).isoformat()
        try:
            path = get_catalog(db_path).path
            with database(path) as c:
                c.execute("DELETE FROM copilot_messages WHERE session_id=?", (self.session_id,))
        except Exception:
            pass


# In-memory thread cache
_SESSIONS: Dict[str, ResearchCopilotSession] = {}


def get_or_create_copilot_session(session_id: str, persona_id: str = "uap", db_path: Optional[str] = None) -> ResearchCopilotSession:
    """Retrieves or initializes a persistent session thread, reading from SQLite on cold boot."""
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
    if session_id in _SESSIONS:
        return _SESSIONS[session_id]

    # Cold start recovery from SQLite
    try:
        path = get_catalog(db_path).path
        ensure_copilot_tables(path)
        with database(path) as c:
            row = c.execute("SELECT persona_id, title, created_at, updated_at FROM copilot_sessions WHERE session_id=?", (session_id,)).fetchone()
            if row:
                session = ResearchCopilotSession(session_id=session_id, persona_id=row[0], title=row[1])
                session.created_at = row[2]
                session.updated_at = row[3]
                msgs = c.execute("SELECT role, content, timestamp FROM copilot_messages WHERE session_id=? ORDER BY id ASC", (session_id,)).fetchall()
                session.messages = [{"role": m[0], "content": m[1], "timestamp": m[2]} for m in msgs]
                _SESSIONS[session_id] = session
                return session
    except Exception:
        pass

    session = ResearchCopilotSession(session_id=session_id, persona_id=persona_id)
    _SESSIONS[session_id] = session
    return session


def create_new_copilot_session(persona_id: str = "uap", db_path: Optional[str] = None) -> ResearchCopilotSession:
    """Explicitly initializes a brand-new session thread."""
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    session = ResearchCopilotSession(session_id=session_id, persona_id=persona_id)
    _SESSIONS[session_id] = session
    try:
        path = get_catalog(db_path).path
        ensure_copilot_tables(path)
        with database(path) as c:
            c.execute("""
                INSERT INTO copilot_sessions (session_id, persona_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (session.session_id, session.persona_id, session.title, session.created_at, session.updated_at))
    except Exception:
        pass
    return session


def list_copilot_sessions(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns overview of all active chat sessions, merging persistent SQLite rows with in-memory sessions."""
    sessions_by_id = {}
    try:
        path = get_catalog(db_path).path
        ensure_copilot_tables(path)
        with database(path) as c:
            rows = c.execute("""
                SELECT s.session_id, s.title, s.persona_id, s.created_at, s.updated_at,
                       COUNT(m.id) as message_count,
                       SUM(CASE WHEN m.role='user' THEN 1 ELSE 0 END) as user_turns
                FROM copilot_sessions s
                LEFT JOIN copilot_messages m ON s.session_id = m.session_id
                GROUP BY s.session_id
            """).fetchall()
            for r in rows:
                sessions_by_id[r[0]] = {
                    "session_id": r[0],
                    "title": r[1],
                    "persona_id": r[2],
                    "created_at": r[3],
                    "updated_at": r[4],
                    "message_count": r[5] or 0,
                    "user_turns": r[6] or 0,
                }
    except Exception:
        pass

    # Merge active in-memory sessions (in-memory has latest updates)
    for s in _SESSIONS.values():
        user_msgs = [m for m in s.messages if m.get("role") == "user"]
        sessions_by_id[s.session_id] = {
            "session_id": s.session_id,
            "title": s.title,
            "persona_id": s.persona_id,
            "message_count": len(s.messages),
            "user_turns": len(user_msgs),
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }

    res = list(sessions_by_id.values())
    res.sort(key=lambda x: x["updated_at"], reverse=True)
    return res


def delete_copilot_session(session_id: str, db_path: Optional[str] = None) -> bool:
    """Deletes a session thread from SQLite and in-memory cache."""
    deleted = False
    if session_id in _SESSIONS:
        del _SESSIONS[session_id]
        deleted = True
    try:
        path = get_catalog(db_path).path
        ensure_copilot_tables(path)
        with database(path) as c:
            c.execute("DELETE FROM copilot_messages WHERE session_id=?", (session_id,))
            c.execute("DELETE FROM copilot_sessions WHERE session_id=?", (session_id,))
            deleted = True
    except Exception:
        pass
    return deleted
