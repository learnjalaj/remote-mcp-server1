import os
import aiosqlite
import asyncio
from pathlib import Path
from fastmcp import FastMCP

# -----------------------------
# Persistent, writable database location
# -----------------------------
DATA_DIR = Path.home() / ".expense_tracker"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "expenses.db"
print("Using database at:", DB_PATH)  # Confirm path at startup

# -----------------------------
# MCP server
# -----------------------------
mcp = FastMCP("ExpenseTracker", port=6280)

# -----------------------------
# Async DB initialization
# -----------------------------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        await db.commit()
    print("Database initialized successfully.")

# -----------------------------
# MCP tools
# -----------------------------
@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
            (date, amount, category, subcategory, note)
        )
        await db.commit()
        return {"status": "ok", "id": cursor.lastrowid}

@mcp.tool()
async def list_expenses(start_date, end_date):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, date, amount, category, subcategory, note "
            "FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC",
            (start_date, end_date)
        )
        rows = await cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, r)) for r in rows]

# -----------------------------
# Run MCP server
# -----------------------------
if __name__ == "__main__":
    # Initialize DB before starting MCP
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_db())

    # Start MCP server
    mcp.run()
