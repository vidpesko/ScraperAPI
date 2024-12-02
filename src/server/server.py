"""
Main RPC server code.

RPC server tasks:
    1. Listen on specified queue for incoming URLs
    2. Open global browser instance
    3. When URL is received, it should use Nodriver and browser instance to retrieve HTML of that page and return it to the client
"""

import asyncio
import aiormq
import aiormq.abc

from nodriver_custom import NodriverCustom


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


async def on_message(message: aiormq.abc.DeliveredMessage):
    global browser

    url = message.body.decode("ascii")
    print("Got url:", url)

    page = await browser.get(url)

    await page.select(".GO-OglasThumb")

    content = await page.get_content()
    # content = "hello"

    response = content.encode()

    await message.channel.basic_publish(
        response,
        routing_key=message.header.properties.reply_to,
        properties=aiormq.spec.Basic.Properties(
            correlation_id=message.header.properties.correlation_id
        ),
    )

    await message.channel.basic_ack(message.delivery.delivery_tag)
    print("Request complete")


class RPCServer:
    async def start_server(self, url: str):
        """Start RPC server listening on specified queue

        Args:
            url (str): url of the message broker
        """
        # Perform connection
        connection = await aiormq.connect(url)

        # Creating a channel
        channel = await connection.channel()

        # Declaring queue
        declare_ok = await channel.queue_declare("rpc_queue")

        # Start listening the queue with name 'hello'
        await channel.basic_consume(declare_ok.queue, on_message)

    @classmethod
    async def setup(cls, queue: str, rabbitmq_url: str):
        """
        Initialise a RPC server. It opens up a browser and start listening for URLs on specified queue
        """

        # Open a browser
        cls.browser = await NodriverCustom.open_browser()

        # Start RPC server

        return cls


QUEUE_NAME = "rnd_queue"
URL = "ampq://localhost/"

async def main():
    server = await RPCServer.setup(QUEUE_NAME, URL)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # we enter a never-ending loop that waits for data
    # and runs callbacks whenever necessary.
    print(" [x] Awaiting RPC requests")
    loop.run_forever()
