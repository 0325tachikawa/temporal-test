from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import compose_greeting


@workflow.defn
class GreetingWorkflow:
    def __init__(self) -> None:
        self._pending_names: list[str] = []
        self._greetings: list[str] = []
        self._exit = False

    @workflow.run
    async def run(self) -> list[str]:
        while True:
            await workflow.wait_condition(
                lambda: bool(self._pending_names) or self._exit
            )

            while self._pending_names:
                name = self._pending_names.pop(0)
                greeting = await workflow.execute_activity(
                    compose_greeting,
                    name,
                    start_to_close_timeout=timedelta(seconds=10),
                )
                self._greetings.append(greeting)

            if self._exit:
                return self._greetings

    @workflow.signal
    def submit_name(self, name: str) -> None:
        self._pending_names.append(name)

    @workflow.signal
    def exit(self) -> None:
        self._exit = True

    @workflow.query
    def get_greetings(self) -> list[str]:
        return list(self._greetings)

    @workflow.query
    def get_pending(self) -> list[str]:
        return list(self._pending_names)
