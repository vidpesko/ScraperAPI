"""
Script to set server parameters and then start it from CLI
"""

import sys, argparse, asyncio

from server import RPCServer


# Default settings
RABBITMQ_URL = "amqp://localhost/"
QUEUE_NAME = "scraper_api_queue"


async def run():
    server = await RPCServer.setup(QUEUE_NAME, RABBITMQ_URL)

loop = asyncio.get_event_loop()
loop.create_task(run())

# we enter a never-ending loop that waits for data
# and runs callbacks whenever necessary.
loop.run_forever()
