from analytics.application.shared.event_handler_interface import IEventHandler
from analytics.domain.events.kafka_event import KafkaEvent


class EventDispatcher:

    def __init__(
        self,
        handlers: list[IEventHandler],
    ) -> None:

        self._handlers = {
            handler.event_type: handler
            for handler in handlers
        }

    async def dispatch(self, event: KafkaEvent) -> None:

        handler = self._handlers.get(event.event_type)

        if handler is None:
            raise ValueError(
                f"No handler registered for event: {event.event_type}"
            )

        await handler.handle(event)
