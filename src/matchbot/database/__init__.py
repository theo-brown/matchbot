import asyncpg
from time import time


async def new_pool(host: str, port: int, user: str, password: str, database_name: str, timeout=5):
    start_time = time()
    pool = None

    while pool is None and time() - start_time < timeout:
        try:
            pool = await asyncpg.create_pool(host=host,
                                             port=port,
                                             user=user,
                                             password=password,
                                             database=database_name,
                                             timeout=timeout)
        except ConnectionRefusedError:
            continue

    return pool