import os
import aiosqlite
import asyncio
from pathlib import Path
from fastmcp import FastMCP

# -----------------------------
# Persistent, writable database location
# -----------------------------
DB_PATH = Path.home() / ".expense_tracker/expenses.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
print("Using database at:", DB_PATH)

# -----------------------------
# MCP server
# -----------------------------
mcp = FastMCP("ExpenseTracker", port=6280)

# -----------------------------
# Global DB connection (shared)
# -----------------------------
db_conn: aiosqlite.Connection | None = None

async def init_db():
    global db_conn
    db_conn = await aiosqlite.connect(DB_PATH)
    await db_conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            note TEXT DEFAULT ''
        )
    """)
    await db_conn.commit()
    print("Database initialized successfully.")

# -----------------------------
# MCP tools
# -----------------------------
@mcp.tool()
async def add_expense(date, amount, category, subcategory="", note=""):
    global db_conn
    async with db_conn.execute(
        "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)",
        (date, amount, category, subcategory, note)
    ) as cursor:
        await db_conn.commit()
        return {"status": "ok", "id": cursor.lastrowid}

@mcp.tool()
async def list_expenses(start_date, end_date):
    global db_conn
    async with db_conn.execute(
        "SELECT id, date, amount, category, subcategory, note "
        "FROM expenses WHERE date BETWEEN ? AND ? ORDER BY id ASC",
        (start_date, end_date)
    ) as cursor:
        rows = await cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, r)) for r in rows]

# -----------------------------
# Run MCP server
# -----------------------------
if __name__ == "__main__":
    async def main():
        await init_db()
        mcp.run()

    asyncio.run(main())
