
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import Database # type: ignore

async def reset_jobs():
    print("Resetting jobs, logs, and billing results...")
    db = Database()
    await db.connect()
    
    # Delete all from dependent tables first
    await db.conn.execute("DELETE FROM agent_logs")
    await db.conn.execute("DELETE FROM booking_results")
    await db.conn.execute("DELETE FROM jobs")
    
    await db.conn.commit()
    await db.close()
    print("✅ All previous jobs and history cleared.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(reset_jobs())
