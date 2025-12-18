import os
import aiosqlite
import tempfile
import asyncio
from pathlib import Path
from fastmcp import FastMCP

# -----------------------------
# Writable database location
# -----------------------------
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "expense_tracker"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "expenses.db"

mcp = FastMCP("ExpenseTracker", port=6280)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as c:
        await c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        await c.commit()

@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    """Add an expense entry into the database"""
    async with aiosqlite.connect(DB_PATH) as c:
        cur = await c.execute(
            """
            INSERT INTO expenses(date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (date, amount, category, subcategory, note),
        )
        await c.commit()
        return {"status": "ok", "id": cur.lastrowid}

@mcp.tool()
async def list_expenses(start_date, end_date):
    """List all expense entries from the database"""
    async with aiosqlite.connect(DB_PATH) as c:
        cur = await c.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date),
        )
        rows = await cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())
    mcp.run()
