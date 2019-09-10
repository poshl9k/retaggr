from retaggr.config import ReverseSearchConfig

# Boorus
from retaggr.engines.danbooru import Danbooru
from retaggr.engines.e621 import E621
from retaggr.engines.iqdb import Iqdb
from retaggr.engines.paheal import Paheal
from retaggr.engines.saucenao import SauceNao

# Exceptions
from retaggr.errors import MissingAPIKeysException, NotAValidEngineException

class ReverseSearch:
    r"""Core class used for Reverse Searching. 
    
    This class can only be instantiated with a :class:`ReverseSearchConfig` instance.

    All listed methods can only be ran from an asynchronous context.

    :ivar accessible_engines: The accessible boorus from the passed in configuration object.
    :param config: The config object.
    :type config: ReverseSearchConfig
    """
    _all_engines = [
        "danbooru",
        "e621",
        "iqdb",
        "paheal",
        "saucenao"
        ]

    def __init__(self, config):
        self.config = config
        self.accessible_engines = {}

        if hasattr(self.config, "min_score"):
            if hasattr(self.config, "danbooru_username") and hasattr(self.config, "danbooru_api_key"):
                self.accessible_engines["danbooru"] = Danbooru(self.config.danbooru_username, self.config.danbooru_api_key, self.config.min_score)
            if hasattr(self.config, "e621_username") and hasattr(self.config, "app_name") and hasattr(self.config, "version"):
                self.accessible_engines["e621"] = E621(self.config.e621_username, self.config.app_name, self.config.version, self.config.min_score)
            self.accessible_engines["iqdb"] = Iqdb(self.config.min_score)

        if hasattr(self.config, "saucenao_api_key"):
            self.accessible_engines["saucenao"] = SauceNao(self.config.saucenao_api_key)

        self.accessible_engines["paheal"] = Paheal()

    async def reverse_search(self, url, callback=None, download=False):
        r"""
        .. deprecated:: 1.2
            Use :meth:`ReverseSearch.search_image_source` instead
        """
        tags = set()
        result = await self.search_image_source(url, callback)
        tags.update(result["tags"])
        return tags

    async def search_image_source(self, url, callback=None, download=False, skip_saucenao=False):
        """
        Reverse searches all accessible boorus for ``url``.

        .. note::
            Callback is a callback function that can be passed in. This can be used to keep track of
            progress for certain methods and functions.

            .. code-block:: python
               :linenos:

                async def callback(booru, tags, source):
                    print("This booru was searched: %s", booru)
                    print("These tags were found: %s", tags)
                    print("This source was found: %s", source)

                # Callback will be called each time a search finishes.
                rs.reverse_search(url, callback)

        After a reverse search, this method will be called with the booru name that was just searched.

        :param url: The URL to search.
        :type url: str
        :param callback: Callback function.
        :type callback: Optional[function]
        :param download: Run searches on boorus that require a file download. Defaults to False.
        :type download: Optional[bool]
        :return: A dictionary with two keys. ``source`` contains a Set of Strings linking to the image source. ``tags`` contains a Set of tags.
        :rtype: dict[Set[str], Set[str]]
        """
        tags = set()
        source = set()
        for booru in self.accessible_engines:
            if self.accessible_engines[booru].download_required:
                if not download:
                    continue
            result = await self.search_image(booru, url)
            tags.update(result["tags"])
            if result["source"]:
                source.update(result["source"])
            if callback:
                await callback(booru, set(result["tags"]), result["source"])
        return {"tags": tags, "source": source}

    async def search_image(self, booru, url):
        r"""Reverse search a booru for ``url``.

        :param booru: Booru to search, this must match a filename in the boorus folder.
        :type booru: str
        :param url: The URL to search.
        :type url: str
        :raises MissingAPIKeysException: Required keys in config object missing.
        :raises NotAValidBooruException: The passed in booru is not a valid booru.
        :return: A set of tags
        :rtype: Set[str]
        """
        if booru not in self._all_engines:
            raise NotAValidEngineException("%s is not a valid engine", booru)
        if booru not in self.accessible_engines:
            raise MissingAPIKeysException("%s is misisng one or more needed API keys. Check the documentation.")
        return await self.accessible_engines[booru].search_image(url)
