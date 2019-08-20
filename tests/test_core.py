import pytest
import retaggr
import os

# Grab the relevant keys from the environment
danbooru_username = os.environ.get('DANBOORU_USERNAME', None)
danbooru_api_key = os.environ.get('DANBOORU_API_KEY', None)
e621_username = os.environ.get('E621_USERNAME', None)
app_name = os.environ.get('APP_NAME', None)
version = os.environ.get('APP_VERSION', None)
if not all([danbooru_username, danbooru_api_key, e621_username, app_name, version]):
    raise ValueError("Missing Environment variables")
config = retaggr.ReverseSearchConfig(danbooru_username=danbooru_username, danbooru_api_key=danbooru_api_key, e621_username=e621_username, app_name=app_name, version=version)

def test_core_creation():
    core = retaggr.ReverseSearch(config)
    assert core.config == config

@pytest.mark.asyncio
async def test_core_search_image_not_a_booru():
    core = retaggr.ReverseSearch(config)
    with pytest.raises(retaggr.NotAValidBooruException):
        await core.search_image("nO", "irrelevant")

@pytest.mark.asyncio
async def test_core_search_image_not_all_api_keys():
    core = retaggr.ReverseSearch(retaggr.ReverseSearchConfig()) # Since we need a core without the config for this
    with pytest.raises(retaggr.MissingAPIKeysException):
        await core.search_image("danbooru", "irrelevant")

@pytest.mark.asyncio
async def test_image_core():
    core = retaggr.ReverseSearch(config)
    tags = await core.search_image("paheal", "https://iris.paheal.net/_images/f0a277f7c4e80330b843f8002daf627e/1876780%20-%20Dancer_of_the_Boreal_Valley%20Dark_Souls%20Dark_Souls_3%20Sinensian.jpg")
    assert tags == ['Dancer_of_the_Boreal_Valley', 'Dark_Souls', 'Dark_Souls_3', 'Sinensian']

@pytest.mark.asyncio
async def test_reverse_search():
    core = retaggr.ReverseSearch(config)
    tags = await core.search_image("paheal", "https://iris.paheal.net/_images/f0a277f7c4e80330b843f8002daf627e/1876780%20-%20Dancer_of_the_Boreal_Valley%20Dark_Souls%20Dark_Souls_3%20Sinensian.jpg")
    assert tags == ['Dancer_of_the_Boreal_Valley', 'Dark_Souls', 'Dark_Souls_3', 'Sinensian']