from logging import getLogger
from typing import Any, Optional

from aiohttp import ClientSession


logger = getLogger(__name__)

class MySession:
    def __init__(self) -> None:
        self._session = ClientSession()

    async def post(self, url: str, json: Optional[Any] = None, **kwargs):
        """
        Perform HTTP POST request.
        """
        async with self._session.post(url, json=json, **kwargs) as response:
            try:
                return (response.status, await response.json(content_type=None))
            except Exception as e:
                logger.exception("Error json parse: %s", e)

    async def get(self, url: str, json: Optional[Any] = None, **kwargs):
        """
        Perform HTTP GET request.
        """
        async with self._session.get(url, json=json, **kwargs) as response:
            try:
                return (response.status, await response.json(content_type=None))
            except Exception as e:
                logger.exception("Error json parse: %s", e)
    
    async def patch(self, url: str, json: Optional[Any] = None, **kwargs):
        """
        Perform HTTP PATCH request.
        """
        async with self._session.patch(url, json=json, **kwargs) as response:
            try:
                return (response.status, await response.json(content_type=None))
            except Exception as e:
                logger.exception("Error json parse: %s", e)
    
    async def delete(self, url: str, json: Optional[Any] = None, **kwargs):
        """
        Perform HTTP DELETE request.
        """
        async with self._session.delete(url, json=json, **kwargs) as response:
            try:
                return (response.status, await response.json(content_type=None))
            except Exception as e:
                logger.exception("Error json parse: %s", e)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.close()

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()
