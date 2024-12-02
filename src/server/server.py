"""
Main RPC server code.

RPC server tasks:
    1. Listen on specified queue for incoming URLs
    2. Open global browser instance
    3. When URL is received, it should use Nodriver and browser instance to retrieve HTML of that page and return it to the client
"""

import asyncio, time, warnings
from typing import Callable

import aiormq
from aiormq.abc import DeliveredMessage

from nodriver_custom import NodriverCustom


warnings.filterwarnings("ignore", category=DeprecationWarning)


browser = None  # Global browser instance


class RPCServer:
    def __init__(self):
        self.rabbitmq_url: str | None = None
        self.queue: str | None = None

    @staticmethod
    async def on_message(message: DeliveredMessage):
        start_time = time.perf_counter()

        global browser

        url = message.body.decode()
        print(" [x] New message:", url)

        # page = await browser.get(url)

        # await page.select(".GO-OglasThumb")

        # content = await page.get_content()
        # response = content.encode()

        await message.channel.basic_publish(
            b"response",
            routing_key=message.header.properties.reply_to,
            properties=aiormq.spec.Basic.Properties(
                correlation_id=message.header.properties.correlation_id
            ),
        )

        await message.channel.basic_ack(message.delivery.delivery_tag)
        print(f" [x] Request completed in {time.perf_counter() - start_time} seconds")

    async def setup_server(self, queue: str | None = None, on_message: Callable | None = None):
        """Starts an RPC server

        Args:
            queue (str | None): name of the queue to listen on. Defaults to self.queue.
            on_message (Callable | None): url of the message broker. Defaults to self.on_message method.
        """

        queue = queue if queue else self.queue

        if not queue:
            raise Exception("No queue was specified for RPC Server to listen on")

        on_message = on_message if on_message else self.on_message

        # Perform connection
        print(f"Connecting to the server ['{self.rabbitmq_url}']")
        connection = await aiormq.connect(self.rabbitmq_url)
        print("Connected!")
        # Creating a channel
        channel = await connection.channel()
        # Declaring queue
        declare_ok = await channel.queue_declare(queue)
        # Start listening the queue with name 'hello'
        await channel.basic_consume(declare_ok.queue, on_message)

    @classmethod
    async def setup(cls, queue: str, rabbitmq_url: str):
        """
        Initialise a RPC server. It opens up a browser and start listening for URLs on specified queue
        """

        # Open a browser
        global browser
        browser = await NodriverCustom().open_browser()

        # Start RPC server
        cls.queue = queue
        cls.rabbitmq_url = rabbitmq_url

        await cls.setup_server(cls)

        print(" [~] Awaiting RPC requests")

        return cls


if __name__ == "__main__":
    async def main():
        QUEUE_NAME = "rnd_queue"
        URL = "amqp://localhost/"
        server = await RPCServer.setup(QUEUE_NAME, URL)

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # we enter a never-ending loop that waits for data
    # and runs callbacks whenever necessary.
    loop.run_forever()
