import asyncio


async def worker():
    print("Worker started")
    await asyncio.sleep(10)
    print("Worker finished")


async def main():
    try:
        async with asyncio.timeout(5):
            await worker()
    except TimeoutError:
        print("Worker timed out!")


asyncio.run(main())