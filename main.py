import os
import sqlite3
import aiosqlite
from pathlib import Path
from fastmcp import FastMCP

# -----------------------------
# Persistent database path
# -----------------------------
DB_PATH = Path.home() / ".expense_tracker/expenses.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
print("Using database at:", DB_PATH)

# -----------------------------
# Initialize DB synchronously
# -----------------------------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        conn.commit()
    print("Database initialized successfully.")

init_db()  # Run before MCP starts

# -----------------------------
# MCP server
# -----------------------------
mcp = FastMCP("ExpenseTracker", port=6280)

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
    mcp.run()
