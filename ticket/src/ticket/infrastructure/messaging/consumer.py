from confluent_kafka import Consumer, KafkaError

from ticket.application.interfaces.processed_event_repository_interface import (
    IProcessedEventRepository,
)
from ticket.application.events.kafka_event import KafkaEvent
from ticket.application.events.ticket_created_event import TicketCreatedEvent
from ticket.application.assignment.assignment_service_interface import (
    IAssignmentService,
)
from ticket.application.shared.application_exception import ApplicationException
from ticket.application.shared.date_time_provider_interface import (
    IDateTimeProvider,
)
from ticket.domain.event.entity.processed_event_entity import ProcessedEventEntity
from ticket.domain.shared.domain_exception import DomainException
from ticket.application.shared.unit_of_work_interface import IUnitOfWork


class Dispatcher:

    def __init__(
        self,
        processed_event_repository: IProcessedEventRepository,
        assignment_service: IAssignmentService,
        datetime_provider: IDateTimeProvider,
        unit_of_work: IUnitOfWork,
    ):
        self.processed_event_repository = processed_event_repository
        self.assignment_service = assignment_service
        self.datetime_provider = datetime_provider
        self.unit_of_work = unit_of_work

        self.consumer = Consumer({
            "bootstrap.servers": "localhost:9092",
            "group.id": "ticket-assignment-dispatch",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
            "enable.auto.offset.store": False,
        })

    async def start(self) -> None:
        self.consumer.subscribe(["ticket.events"])

        print("Assignment dispatch consumer started...")

        try:
            while True:
                message = self.consumer.poll(1.0)

                if message is None:
                    continue

                error = message.error()

                if error is not None:
                    if error.code() == KafkaError._PARTITION_EOF:
                        continue

                    raise RuntimeError(f"Kafka error: {error}")

                try:
                    payload = message.value()

                    if payload is None:
                        raise ValueError("Kafka message payload is empty")

                    # Decode the common envelope without validating
                    # the event-specific data yet.
                    envelope = KafkaEvent[dict].model_validate_json(payload)

                    # This consumer only handles ticket.created.
                    if envelope.event_type != "ticket.created":
                        print(f"Ignoring event: {envelope.event_type}")

                        self.consumer.commit(
                            message=message,
                            asynchronous=False,
                        )
                        continue

                    event = KafkaEvent[
                        TicketCreatedEvent
                    ].model_validate_json(payload)

                    print(f"Received ticket.created: {event.id}")

                    # Check idempotency.
                    processed = await self.processed_event_repository.exists(
                        event_id=event.id
                    )

                    if processed:
                        print(f"Event already processed: {event.id}")

                        self.consumer.commit(
                            message=message,
                            asynchronous=False,
                        )
                        continue

                    # Process the event.
                    processed_event = ProcessedEventEntity.create(
                        event_id=event.id,
                        event_type=event.event_type,
                        processed_at=self.datetime_provider.now(),
                    )

                    await self.processed_event_repository.add(
                        event=processed_event
                    )

                    await self.assignment_service.dispatch(
                        ticket_id=event.data.ticket_id
                    )

                    # Commit database transaction first.
                    await self.unit_of_work.commit()

                    # Commit Kafka offset only after successful processing.
                    self.consumer.commit(
                        message=message,
                        asynchronous=False,
                    )

                    print(f"Successfully processed event: {event.id}")

                except (ApplicationException, DomainException) as exc:
                    await self.unit_of_work.rollback()

                    print(f"Event processing failed: {exc}")

                    # Do not commit the offset.
                    # The message can be processed again.

                except Exception as exc:
                    await self.unit_of_work.rollback()

                    print(f"Unexpected consumer error: {exc}")

                    raise

        finally:
            self.consumer.close()
