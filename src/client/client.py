import asyncio, uuid

import aiormq, pika
from aiormq.abc import DeliveredMessage


class ClientBase:
    def __init__(self, connection_url: str, listen_queue: str):
        self.connection_url = connection_url
        self.listen_queue = listen_queue
        self.callback_queue = ""


class AsyncScraperApiClient(ClientBase):
    def __init__(self, connection_url, listen_queue, event_loop):
        super().__init__(connection_url, listen_queue)

        self.connection: aiormq.Connection = None
        self.channel: aiormq.Connection = None
        self.futures = {}
        self.loop = event_loop

    async def connect(self):
        self.connection = await aiormq.connect(self.connection_url)

        self.channel = await self.connection.channel()
        declare_ok = await self.channel.queue_declare(exclusive=True, auto_delete=True)

        await self.channel.basic_consume(declare_ok.queue, self.on_response)

        self.callback_queue = declare_ok.queue

    async def on_response(self, message: DeliveredMessage):
        future = self.futures.pop(message.header.properties.correlation_id)
        future.set_result(message.body.decode())

    async def get(self, url: str):
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.basic_publish(
            str(url).encode(),
            routing_key=self.listen_queue,
            properties=aiormq.spec.Basic.Properties(
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=self.callback_queue,
            ),
        )

        return await future


class ScraperApiClient(ClientBase):
    def __init__(self, connection_url, listen_queue):
        super().__init__(connection_url, listen_queue)

        self.connection: pika.BlockingConnection = None
        self.response = None
        self.corr_id = None

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def get(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange="",
            routing_key=self.listen_queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(n),
        )
        while self.response is None:
            self.connection.process_data_events(time_limit=None)
        return self.response.decode()


if __name__ == "__main__":
    # Async code

    # loop = asyncio.get_event_loop()

    # async def main():
    #     client = AsyncScraperApiClient("amqp://localhost/", "avtonet_api_queue", loop)
    #     await client.connect()

    #     response = await client.get(
    #         "https://www.avto.net/Ads/details.asp?id=20336915&display=Mercedes-Benz%20GLE-Razred"
    #     )
    #     print(response[:10])


    # loop.run_until_complete(main())


    # Sync code

    client = ScraperApiClient("amqp://localhost/", "avtonet_api_queue")
    client.connect()

    response = client.get(
        "https://www.avto.net/Ads/details.asp?id=20336915&display=Mercedes-Benz%20GLE-Razred"
    )

    # print(response)
