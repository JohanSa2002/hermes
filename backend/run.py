"""
Arranque local para Windows + Python 3.14.
psycopg3 requiere SelectorEventLoop; este script lo configura
antes de que uvicorn tome el control del event loop.
"""
import asyncio
import selectors
import uvicorn


async def main():
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
