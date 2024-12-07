# ScraperAPI
Easily scrape websites protected by Cloudflare Bot Managment (or websites that require JS to load)

## Why?
You might be asking, what is the purpose of this package, when other similar packages exist (like nodriver and undetected-chromedriver). The problem with packages like nodriver is, that they do not work well for real-time scraping.

Example of scraping with nodriver:
``
import nodriver as uc

async def main():

    browser = await uc.start()
    page = await browser.get('https://www.nowsecure.nl')
    html = await page.get_content()

uc.loop().run_until_complete(main())  # Execution time is around 2 seconds
``

If we were to build API around this code, users would have to wait 2 or more seconds for every request.

## The solution
If we profile previous code we see, that most of the time is spent waiting for browser window to open. If the website has many images and other resource-intensive content, then a big chunk of time is spent waiting for page to load. First problem is solved by launching one global browser instance and fetching all requests through it. This is implemented using RPC for inter-process communication. You start the server, which launches browser and then using ScraperAPIClient class you connect to it and execute requests. Server uses AMQP standard. Second problem is solved with disabling images and JS to load. These two steps drastically reduce the amount of time for each get request (from 2 seconds to 0.4 on average)

## How does it work?

1. You start the server with `scraperapi-start <url> <queue_name>`
2. You connect to the server and execute get request

## Example
Simple get request:
``
from scraperapi.client import ScraperApiClient

client = ScraperApiClient("amqp://localhost/", "request_queue")
client.connect()

response = client.get("https://www.nowsecure.nl")
``