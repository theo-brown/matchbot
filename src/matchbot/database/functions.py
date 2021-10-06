from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine


def new_engine(host: str, port: int, user: str, password: str, db_name: str) -> AsyncEngine:
    return create_async_engine(f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}',
                               echo=True,  future=True)


def new_session(engine: AsyncEngine) -> AsyncSession:
    return AsyncSession(engine, expire_on_commit=False)
