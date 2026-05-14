import asyncio
import sys

from temporalio.client import Client

from workflows import GreetingWorkflow

WORKFLOW_ID = "greeting-workflow"


async def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "greetings"

    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle_for(GreetingWorkflow.run, WORKFLOW_ID)

    if target == "pending":
        result = await handle.query(GreetingWorkflow.get_pending)
        print(f"Pending names: {result}")
    elif target == "greetings":
        result = await handle.query(GreetingWorkflow.get_greetings)
        print(f"Greetings: {result}")
    else:
        print(f"Unknown query target: {target}")
        print("Usage: python send_query.py [greetings|pending]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
