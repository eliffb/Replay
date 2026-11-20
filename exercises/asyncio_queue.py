
import asyncio


async def worker(name: str, queue: asyncio.Queue[str]) -> None:
    while True:
        item = await queue.get()

        try:
            print(f"Worker {name} processing: {item}")
            await asyncio.sleep(1)
            print(f"Worker {name} finished: {item}")
        finally:
            queue.task_done()


async def main() -> None:
    queue = asyncio.Queue()

    tasks = [
        asyncio.create_task(worker("A", queue)),
        asyncio.create_task(worker("B", queue)),
    ]

    for item in ["Task A", "Task B", "Task C"]:
        queue.put_nowait(item)

    await queue.join() #queue.join() bütün görevlerin tamamlanmasını bekler.

    for task in tasks: #İşler bitince worker'lara cancellation gönderilir.
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True) 
    #gather() iptallerin tamamlanmasını bekler.


if __name__ == "__main__":
    asyncio.run(main())
