"""
Custom wrapper around Nodriver package to optimise speed

Features:
    - When started, it prevents pages from loading JS and images
    - Allows for easy use use of proxy network
    - if demand increases, it can open more browser windows
"""

import asyncio

import nodriver as uc


class BrowserHandler:
    def __init__(self):
        self.browsers: list[uc.Browser] = []

    async def disable_image_loading(self, browser: uc.Browser):
        page = await browser.get("chrome://settings/content/images")
        elem = await page.find("Don't allow sites to show images", best_match=True)
        await elem.click()

    async def disable_js_loading(self, browser: uc.Browser):
        page = await browser.get("chrome://settings/content/javascript")
        elem = await page.find("Don't allow sites to use JavaScript", best_match=True)
        await elem.click()

    async def open_browser(self, disable_resources=True):
        """Opens a new Chrome browser

        Args:
            disable_resources (bool, optional): If you wish to disable page resources, like JS and images. Defaults to True.
        """
        browser = await uc.start()

        if disable_resources:
            await self.disable_image_loading(browser)
            await self.disable_js_loading(browser)

        self.browsers.append(browser)

    async def get(self, url: str, return_html: bool = False, scraper_params: dict = None) -> uc.Tab | str:
        browser = self.browsers[0]
        page = await browser.get(url)

        if scraper_params.get("wait_for", False):
            await page.select(scraper_params["wait_for"])
        # Other parameters ...

        return await page.get_content() if return_html else page

if __name__ == "__main__":
    async def main():
        browser = await BrowserHandler.open_browser()
        print(browser)
        # await browser.get("https://www.avto.net/Ads/details.asp?id=20327886")
        # await browser.get("https://httpbin.co/ip")
        # await asyncio.sleep(2)

    uc.loop().run_until_complete(main())