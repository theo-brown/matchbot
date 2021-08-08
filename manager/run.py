import asyncio
from matchbot.manager import Manager

async def main():
    manager = Manager()
    try:
        await manager.start()
    finally:
        await manager.stop()

asyncio.run(main())
