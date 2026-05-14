import asyncio

from temporalio.client import Client

from workflows import GreetingWorkflow

WORKFLOW_ID = "greeting-workflow"
TASK_QUEUE = "greeting-task-queue"


async def main() -> None:
    client = await Client.connect("localhost:7233")

    handle = await client.start_workflow(
        GreetingWorkflow.run,
        id=WORKFLOW_ID,
        task_queue=TASK_QUEUE,
    )

    print(f"Started workflow: id={handle.id}, run_id={handle.first_execution_run_id}")


if __name__ == "__main__":
    asyncio.run(main())
