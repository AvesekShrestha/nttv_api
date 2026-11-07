import asyncio
from datetime import date

from confluent_kafka import Consumer, KafkaError

import ticket
from ticket.application.exceptions.event_exceptions import EventAlreadyProcessed
from ticket.application.interfaces.processed_event_repository_interface import (
    IProcessedEventRepository,
)

from ticket.application.events.kafka_event import KafkaEvent
from ticket.application.events.ticket_created_event import TicketCreatedEvent
from ticket.application.assignment.assignment_service_interface import IAssignmentService
from ticket.application.shared.application_exception import ApplicationException
from ticket.application.shared.date_time_provider_interface import IDateTimeProvider
from ticket.domain.event.entity.processed_event_entity import ProcessedEventEntity
from ticket.domain.shared.domain_exception import DomainException



class Dispatcher:

    def __init__(
        self,
        processed_event_repository : IProcessedEventRepository,
        assignment_service : IAssignmentService,
        datetime_provider : IDateTimeProvider

    ):

        self.processed_event_repository = processed_event_repository
        self.assignment_service = assignment_service
        self.datetime_provider = datetime_provider
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

                    raise RuntimeError(
                        f"Kafka error: {message.error()}"
                    )

                try:
                    payload = message.value()

                    print(payload)
                    if payload is None:
                        raise ValueError("Kafka message payload is empty")

                    event = KafkaEvent[TicketCreatedEvent].model_validate_json(
                            payload
                        )

                    print(event)

                    if event.event_type != "ticket.created":
                        self.consumer.commit(
                            message=message,
                            asynchronous=False,
                        )
                        continue

                    ticket_id = event.data.ticket_id
                    print(f"printing ticket_id from the consumer : {ticket_id}")

                    processed : bool = await self.processed_event_repository.exists(event_id=event.id)

                    if processed:
                        print(f"Event already processed: {event.id}")

                        self.consumer.commit(
                            message=message,
                            asynchronous=False,
                        )
                        continue

                    processed_event = ProcessedEventEntity.create(
                        event_id=event.id,
                        event_type=event.event_type,
                        processed_at=self.datetime_provider.now()
                    )

                    await self.processed_event_repository.add(event=processed_event)
                    await self.assignment_service.dispatch(ticket_id=ticket_id)

                    self.consumer.commit(
                        message=message,
                        asynchronous=False,
                    )

                except (ApplicationException, DomainException) as e:
                    print(f"Printing error message from consumer : {e.message} with status : {e.status}")

                except Exception as exc:
                    print(f"Failed to process Kafka message: {exc}")
                    raise

        finally:
            self.consumer.close()
