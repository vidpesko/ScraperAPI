"""
Client for interacting with server

TODO - If server isn't started and client sends get request, it will freeze. Fix this. Client should inform user that server isn't running.
"""

import uuid, json, time

import aiormq, pika
from aiormq.abc import DeliveredMessage

try:
    from .shared.message_utils import encode_command
except ImportError:
    from shared.message_utils import encode_command  # type: ignore


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

    def get(self, url: str, scraper_params: dict = None, timeout: int = 5) -> dict:
        """Similar to get request: send get request to website via ScraperAPI

        Args:
            url (str): url of website
            scraper_params (dict, optional): additional parameters for scraper. Defaults to None.
            timeout (int): timeout in seconds. If reached, raise TimeoutException. Defaults to 5.

        Raises:
            TimeoutError: if waiting for response tooks longer than specified timeout

        Returns:
            str: HTML of requested website
        """

        if not scraper_params:
            scraper_params = {}


        # Generate command
        command = encode_command(url, scraper_params)

        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange="",
            routing_key=self.listen_queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=command,
        )

        start_time = time.perf_counter()
        while self.response is None:
            self.connection.process_data_events(time_limit=0)

            time_delta = time.perf_counter() - start_time
            if time_delta > timeout:
                raise TimeoutError("Timeout reached. Check if RPC server is really running or try restarting it")

        return json.loads(self.response.decode())


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

    start = time.perf_counter()
    scraper_params = {"wait_fo2r": ".something", "wait_for_timeout": 2}

    client = ScraperApiClient("amqp://localhost/", "avtonet_api_queue")
    client.connect()
    response = client.get(
        "https://www.avto.net/Ads/details.asp?id=20388158&display=BMW%20serija%203%20Touring:",
        scraper_params,
    )

    with open("company.html", "w") as f:
        f.write(response["html"])

    print(time.perf_counter() - start)
