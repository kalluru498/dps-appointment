
import sys
import asyncio
import os



# Add src to path to resolve imports correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    # Set the policy BEFORE any loop is created
    try:
        from asyncio import WindowsProactorEventLoopPolicy, set_event_loop_policy
        set_event_loop_policy(WindowsProactorEventLoopPolicy())
    except ImportError:
        pass

import uvicorn  # type: ignore

if __name__ == "__main__":
    print("Starting DPS Agent (reload disabled for Windows compatibility)...")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=False)  # type: ignore
