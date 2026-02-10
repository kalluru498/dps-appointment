# Fix Report #2

## Issues Fixed

1. **UnicodeEncodeError**:
   - The logging function was attempting to print a special unicode character (`═`) which is not supported by the default Windows console encoding (cp1252).
   - **Fix**: Replaced `═` with standard ASCII `=` in `src/agent/booking_engine.py`.

2. **NotImplementedError (Playwright)**:
   - Playwright requires the `ProactorEventLoop` on Windows to manage subprocesses (browser instances). Uvicorn's reloader can sometimes default to `SelectorEventLoop` or interfere with the loop policy.
   - **Fix**: Added explicit configuration to `src/api/main.py` to enforce `asyncio.WindowsProactorEventLoopPolicy()` on Windows startup.

## Next Steps

1. **Stop the current backend server** (Press `Ctrl+C` in the terminal).
2. **Restart the server**:
   ```bash
   uvicorn api.main:app --reload
   ```
3. **Retry**: Go to the dashboard and click "Start New Job".

The browser should now launch correctly!
