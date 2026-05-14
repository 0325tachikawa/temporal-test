import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import compose_greeting
from workflows import GreetingWorkflow

TASK_QUEUE = "greeting-task-queue"


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[GreetingWorkflow],
        activities=[compose_greeting],
    )

    print(f"Worker started on task queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
