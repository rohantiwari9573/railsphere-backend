import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    # Note: --reload's WatchFiles subprocess bootstrap on Windows
    # doesn't reliably apply this process's asyncio event loop policy
    # to the reloaded child, which breaks the /ws/analytics live
    # NOTIFY listener (app/core/pg_listen.py) specifically -- it
    # silently never receives cross-process notifications under
    # reload=True. Doesn't affect production, which runs via gunicorn
    # without --reload. To test that feature locally, run
    # `uvicorn app.main:app --port 8000` directly (no reload) instead.
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
