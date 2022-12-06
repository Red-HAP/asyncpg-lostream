#  Copyright 2022 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio

import pytest
import pytest_asyncio
import sqlalchemy as sa
import sqlalchemy.event
import sqlalchemy.future
import sqlalchemy.pool
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class Settings:
    database_url = "postgresql+asyncpg://postgres:secret@localhost:5432/postgres"


async def drop_database(connection: AsyncConnection, name: str):
    await connection.execute(sa.text(f'DROP DATABASE IF EXISTS "{name}"'))


async def create_database(connection: AsyncConnection, name: str):
    await drop_database(connection, name)
    await connection.execute(sa.text(f'CREATE DATABASE "{name}"'))


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def default_settings():
    return Settings


@pytest_asyncio.fixture(scope="session")
async def default_engine(default_settings):
    engine = create_async_engine(
        default_settings.database_url,
        isolation_level="AUTOCOMMIT",
        poolclass=sqlalchemy.pool.NullPool,
        future=True,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def db_url(default_settings):
    default_url = sqlalchemy.engine.make_url(default_settings.database_url)
    return default_url.set(database=f"test_{default_url.database}")


@pytest_asyncio.fixture(scope="session")
async def db_engine(default_engine, db_url):
    async with default_engine.connect() as connection:
        await create_database(connection, db_url.database)

    engine = create_async_engine(
        db_url,
        poolclass=sqlalchemy.pool.NullPool,
        future=True,
    )

    yield engine

    await engine.dispose()

    async with default_engine.connect() as connection:
        await drop_database(connection, db_url.database)


@pytest_asyncio.fixture
async def db(db_engine):
    session_factory = sessionmaker(class_=AsyncSession, expire_on_commit=False)

    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        await connection.begin_nested()

        async with session_factory(bind=connection) as session:

            @sqlalchemy.event.listens_for(session.sync_session, "after_transaction_end")
            def reopen_nested_transaction(_session, _transaction):
                if connection.closed:
                    return

                if not connection.in_nested_transaction():
                    connection.sync_connection.begin_nested()

            yield session

            await transaction.rollback()
