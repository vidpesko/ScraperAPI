"""
Custom wrapper around Nodriver package to optimise speed

Features:
    - When started, it prevents pages from loading JS and images
    - Allows for easy use use of proxy network
"""

import asyncio

import nodriver as uc


class NodriverCustom:
    def __init__(self):
        pass

    async def disable_image_loading(self):
        page = await self.browser.get("chrome://settings/content/images")
        elem = await page.find("Don't allow sites to show images", best_match=True)
        await elem.click()

    async def disable_js_loading(self):
        page = await self.browser.get("chrome://settings/content/javascript")
        elem = await page.find("Don't allow sites to use JavaScript", best_match=True)
        await elem.click()

    @classmethod
    async def open_browser(cls, disable_resources=True):
        """Open a Chrome browser and return instance

        Args:
            disable_resources (bool, optional): If you wish to disable page resources, like JS and images. Defaults to True.
        """
        cls.browser = await uc.start()

        if disable_resources:
            await cls.disable_image_loading(cls)
            await cls.disable_js_loading(cls)

        return cls.browser


if __name__ == "__main__":
    async def main():
        browser = await NodriverCustom().open_browser()
        await browser.get("https://www.avto.net/Ads/details.asp?id=20327886")
        await asyncio.sleep(2)

    uc.loop().run_until_complete(main())
