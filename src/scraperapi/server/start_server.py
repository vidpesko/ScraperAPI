"""
Script to set server parameters and then start it from CLI

TODO - handle CLI parameters
"""

import sys, argparse, asyncio

from .server import RPCServer


# Default settings
RABBITMQ_URL = "amqp://localhost/"
QUEUE_NAME = "avtonet_api_queue"


loop = asyncio.get_event_loop()
server = RPCServer.setup(QUEUE_NAME, RABBITMQ_URL)

loop.create_task(server)

# we enter a never-ending loop that waits for data
# and runs callbacks whenever necessary.
try:
    loop.run_forever()
except KeyboardInterrupt:
    print(" [-] Closing server...")
    sys.exit(0)
