import asyncio, uuid

import aiormq
from aiormq.abc import DeliveredMessage


class ScraperApiClient:
    def __init__(self, connection_url: str, listen_queue: str):
        self.connection_url = connection_url
        self.listen_queue = listen_queue

        self.connection: aiormq.Connection = None
        self.channel: aiormq.Connection = None
        self.callback_queue = ""
        self.futures = {}
        self.loop = loop

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
        future = loop.create_future()

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


if __name__ == "__main__":
    async def main():
        client = ScraperApiClient("amqp://localhost/", "scraper_api_queue")
        await client.connect()

        response = await client.get(
            "https://www.avto.net/Ads/details.asp?id=20336915&display=Mercedes-Benz%20GLE-Razred"
        )
        print(response[:10])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
