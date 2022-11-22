# asyncpg-lostream

CRUD on PostgreSQL large objects using async drivers and asyncio. It is tested against SQLAlchemy.

## Purpose

Synchronous drivers such as `psycopg2` support large objects via a file-like interface utilizing libpg. Unfortunately, async drivers such as `asyncpg` do not support large objects at all (at this time). This module is designed to provide an interface for PostgreSQL large objects that is compatible with asyncio and async database drivers. This interface is achieved by calling the supporting PostgreSQL stored functions that are an interface to the large object store.

This interface is designed to operate on data by reading and writing in chunks so as to stream the data to and from the large object store.

This codebase is not tied or affiliated with asyncpg. It does utilize SQLAlchemy's AsyncConnection class in its typing.

## PostgreSQL Large Objects

A large object is a special store in PostgreSQL that operates similarly to a file. The large object itself is the record. The database data type is `bytea` (`bytes` in Python). The interface operates as a read and write to the allocated large object via read and write functions. (There are more, but they are out of scope for this project.) The data type of the large object id is `oid`. The tables used by PostgreSQL are `pg_largeobject` and `pg_largeobject_metadata`. The `pg_largeobject` table holds the data itself. The `pg_largeobject_metadata` has a link to the owner oid. These two tables are linked by the `oid` reference.

When assiciating the large object to a table record, add an `oid` type column to hold the allocated large object `oid` value from a created large object.

See the PostgreSQL documentation [here](https://www.postgresql.org/docs/current/largeobjects.html).

## Utilization

### Explicit Create

```python
from asyncpg_lostream.lostream import PGLargeObject

# It is the responsibility of the caller to resolve how an
# AsyncEngine is created and how an AsyncConnection is created.

# Create a large object
lob_oid = await PGLargeObject.create_large_object(db)

# Open a large object for read and write
pgl = PGLargeObject(async_connection, lob_oid, mode="rw")

with open("my_data.txt", "r") as data:
    for buff in data.read(pgl.chunk_size):
        await pgl.write(buff.encode)

pgl.close()
```

### Context Manager Create

```python
from asyncpg_lostream.lostream import PGLargeObject

# It is the responsibility of the caller to resolve how an
# AsyncEngine is created and how an AsyncConnection is created.

with open("my_data.txt", "r") as data:
    async with PGLargeObject(async_connection, 0, "w") as pgl:
        for buff in data.read(pgl.chunk_size):
            await pgl.write(buff.encode())
```

### Context manager read

```python
from asyncpg_lostream.lostream import PGLargeObject

# It is the responsibility of the caller to resolve how an
# AsyncEngine is created and how an AsyncConnection is created.

async with PGLargeObject(async_connection, existing_lob_oid, "r") as pgl:
    async for buff in pgl:
        print(buff.decode())
```

## Development

### Environment

1. Create a virtual environment
    ```bash
    python -m venv /path/to/venv
    ```
2. Activate the virtual environment
    ```bash
    source /path/to/venv/bin/activate
    ```
3. Ensure pip is up to date
    ```bash
    pip install --upgrade pip
    ```
4. Install packages from `requirements.txt`
    ```bash
    pip install -r requirements.txt
    ```
5. Install `pre-config`
   ```bash
   pre-config install
   ```

### Development

After making changes, create your unit tests in the `asyncpg-lostream/tests` directory.

Test your changes with the command `python -m pytest`


## Packaging

Build the package using `python -m build`. This will put built packages into the `dist/` directory.

For instructions on upload to PyPI, see the [Packaging Python Projects Dcoumentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/#uploading-the-distribution-archives)
