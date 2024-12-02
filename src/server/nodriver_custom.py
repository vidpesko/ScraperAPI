"""
Custom wrapper around Nodriver package to optimise speed

Features:
    - When started, it prevents pages from loading JS and images
    - Allows for easy use use of proxy network
"""

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
        
        return cls

    async def get(self, url: str, wait_for: str | None = None) -> uc.Tab:
        """Navigates to url and retrieves page object

        Args:
            url (str): page url
            wait_for (str | None, optional): using await select() to wait for certain element to load. Should be a valid CSS selector. Defaults to None.
        """
        page = await self.browser.get(url)

        if wait_for:
            await page.select(wait_for)

        return page
    

    async def get_html(self, *args, **kwargs) -> str:
        """
        Retrieve page HTML. Under the hood it calls get() method 
        """
        page = await self.get(*args, **kwargs)
        return await page.get_content()
