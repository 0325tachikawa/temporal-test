import asyncio
import sys

from temporalio.client import Client

from workflows import GreetingWorkflow

WORKFLOW_ID = "greeting-workflow"


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python send_signal.py <name>")
        print("       python send_signal.py exit")
        sys.exit(1)

    arg = sys.argv[1]
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle_for(GreetingWorkflow.run, WORKFLOW_ID)

    if arg == "exit":
        await handle.signal(GreetingWorkflow.exit)
        print("Sent signal: exit")
    else:
        await handle.signal(GreetingWorkflow.submit_name, arg)
        print(f"Sent signal: submit_name({arg!r})")


if __name__ == "__main__":
    asyncio.run(main())
