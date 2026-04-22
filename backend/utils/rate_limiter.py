import asyncio

# Cap concurrent outbound Riot API requests per invocation.
# A new Semaphore is created per get_summoner_data_async call so it
# is safely scoped to a single asyncio event loop.
CONCURRENCY_LIMIT = 5


def make_semaphore() -> asyncio.Semaphore:
    return asyncio.Semaphore(CONCURRENCY_LIMIT)
