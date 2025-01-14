"""
Script to test the ScraperAPI client
"""

import sys
import time

try:
    from .client import ScraperApiClient
except ImportError:
    from client import ScraperApiClient

def test_client():
    if len(sys.argv) < 2:
        raise Exception("Not all parameters have been provided")
    
    url = sys.argv[1]

    start = time.perf_counter()
    scraper_params = {"wait_fo2r": ".something", "wait_for_timeout": 2}

    client = ScraperApiClient("amqp://localhost/", "avtonet_api_queue")
    client.connect()
    response = client.get(
        url,
        scraper_params,
    )

    print("Executed in", time.perf_counter() - start)


if __name__ == "__main__":
    test_client()