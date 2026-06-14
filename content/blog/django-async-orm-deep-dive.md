+++
title = "Django ORM: From sync_to_async Threads to Native psycopg3"
date = "2026-06-13"
slug = "django-orm-from-sync_to_async-threads-to-native-psycopg3"
description = "A deep dive into how Django's ORM became truly async — why the old thread-pool trick was never real async, what changed in Django 6.0 with psycopg3 and ContextVar, and why asyncpg was left out."
tags = [
    "django",
    "python",
    "postgresql",
    "async",
    "performance"
]
+++

Django shipped async ORM methods back in 3.1, and for years I told people they
were not really async. `aget()`, `afilter()`, `acreate()`, the whole `a`-prefixed
surface — the docs called it async support, and in the sense that mattered it was
not. Every one of those calls still blocked a real OS thread. You got coroutine
syntax without coroutine performance.

Django 6.0 fixed it for real in December 2025. I want to walk through the path
from "fake async via threads" to "native async via psycopg3," because it is not
a story about a feature landing. It is a story about three constraints that
boxed Django in for five years: `psycopg2` blocks, connection state lived in
thread-locals, and the entire ORM assumed DB-API2. Once you see those three, every
design decision Django made falls out of them almost mechanically.

## The Old Trick Was Threads Pretending To Be Coroutines

When async views arrived in 3.1, the ORM underneath them was entirely synchronous.
`psycopg2` — the default PostgreSQL driver for most of Django's life — wraps
`libpq`, a C library with no async I/O surface at all. There is no flag you set to
make `psycopg2` async. You either replace the driver or you find a workaround.

Django found the workaround: `asgiref.sync.sync_to_async`.

```python
# Simplified — what aget() actually did under the hood in Django 5.x
from asgiref.sync import sync_to_async

async def aget(self, *args, **kwargs):
    return await sync_to_async(self.get, thread_sensitive=True)(*args, **kwargs)
```

`sync_to_async` pushes the callable into a `ThreadPoolExecutor`. The event loop is
not blocked, because the coroutine awaits the thread's future. But a real OS thread
is blocked, sitting on a TCP socket waiting for Postgres to answer. You moved the
blocking, you did not remove it.

The `thread_sensitive=True` flag is the part that gives the game away. Django's
database connections lived in thread-locals:

```python
# django/db/backends/base/base.py (pre-6.0)
import threading
_thread_local = threading.local()
```

Without `thread_sensitive=True`, two consecutive `sync_to_async` calls from the same
request might land on different threads, see different thread-locals, and tear your
transaction state in half. The flag pins every call within the same coroutine
context to one dedicated thread, so the connection still looks like a single
connection per request. It is a clever illusion. It is still an illusion.

Put it together and the cost is obvious. Five hundred concurrent async requests, each
touching the database, need five hundred threads. That is the thread-per-connection
model that async was supposed to retire, wearing a coroutine costume.

## Why psycopg2 Was a Dead End

You cannot retrofit async I/O onto `psycopg2`. It calls into `libpq` synchronously
and blocks the calling thread until the query returns. The only way to run it in an
async context is exactly what Django did: park it in a thread and await that thread.
There was never a clever escape here.

The obvious alternative was `asyncpg`, a fully async PostgreSQL driver that beats
psycopg3 on raw throughput. Django ruled it out, and the reasons are worth their own
section further down. The short version is that `asyncpg` does not implement DB-API2
(PEP 249)[^1], and Django's ORM is built on DB-API2 from the ground up — cursor
objects, `execute()`, `fetchone()`, `fetchall()`. You do not bolt a different
contract onto twenty years of ORM and call it a driver swap.

`psycopg3` is the answer that fits, because it does not force that choice.

## psycopg3 Does Async And DB-API2 At The Same Time

`psycopg3` — the package is just `psycopg`, not `psycopg3` — was redesigned to support
both synchronous and asynchronous execution through one shared core[^2]. The same query
compilation logic runs both paths. What changes is the connection and cursor type you
hand it.

```python
# psycopg3 — synchronous path
with psycopg.connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM posts WHERE id = %s", [pk])
        row = cur.fetchone()

# psycopg3 — async path (same SQL, same parameters, different objects)
async with await psycopg.AsyncConnection.connect(dsn) as aconn:
    async with aconn.cursor() as cur:
        await cur.execute("SELECT * FROM posts WHERE id = %s", [pk])
        row = await cur.fetchone()
```

`AsyncConnection` and `AsyncCursor` use `asyncio` directly. The `await cur.execute(...)`
suspends the coroutine and releases the event loop while the network I/O happens. No
thread sits idle on a socket. That is the whole difference, and it is the difference
that matters.

Django 6.0 made psycopg3 the recommended PostgreSQL driver and wired
`AsyncConnection` and `AsyncCursor` into the backend.

## What Django 6.0 Actually Changed

Three refactors enabled the switch. None of them are glamorous, and that is the point.

### 1. ContextVar Replaces Thread-Locals

Thread-locals are indexed by thread ID. Coroutines do not have thread IDs of their
own — they share threads and switch between each other at `await` points. So
thread-local connection storage is not merely awkward under async, it is structurally
wrong. Think of a thread-local as a coat hook bolted to a single chair: it works only
as long as one person stays in that chair the whole time. Coroutines stand up and swap
chairs constantly.

The fix is `contextvars.ContextVar`, which arrived in Python 3.7. A `ContextVar` is
scoped to the current execution context, and each asyncio `Task` gets its own context,
copied from its parent when it is created. Django 6.0 moved connection storage off
`threading.local()` and onto a `ContextVar`:

```python
# django/db/backends/base/base.py (Django 6.0)
from contextvars import ContextVar

_connection: ContextVar = ContextVar('django_db_connection', default=None)
```

Two concurrent requests, both awaiting a query, each live in their own asyncio Task,
each with their own context copy, each seeing their own connection. No locking, no
thread affinity, no `thread_sensitive` gymnastics. The coat hook now travels with the
person.

### 2. DatabaseWrapper Gets an Async Connection Path

`DatabaseWrapper` is the Django object that represents a database connection. Before
6.0 it exposed one path, `self.connection`, a synchronous psycopg2 connection. After
6.0 it also exposes `async_connection()`:

```python
# Conceptual — the async context manager on DatabaseWrapper
@asynccontextmanager
async def async_connection(self):
    conn = await psycopg.AsyncConnection.connect(**self.get_connection_params())
    _connection.set(conn)
    try:
        yield conn
    finally:
        await conn.close()
```

Django's connection-handling code detects whether it is running inside an asyncio event
loop and routes to the right path. You do not pick the path. The runtime does.

### 3. SQLCompiler Gets async_execute

The query compiler, `SQLCompiler` and its subclasses, is where Django turns a `QuerySet`
into SQL and sends it to the database. Before 6.0 there was one path, `execute_sql()`.
Django 6.0 adds `async_execute_sql()`:

```python
async def async_execute_sql(self, result_type=MULTI, chunked_fetch=False, chunk_size=GET_ITERATOR_CHUNK_SIZE):
    async with self.connection.async_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(self.as_sql())
            if result_type == MULTI:
                return [row async for row in cursor]
            return await cursor.fetchone()
```

`aget()`, `afilter()`, `aiterator()` and the rest now route through `async_execute_sql()`
instead of wrapping `execute_sql()` in `sync_to_async`. The thread pool drops out of the
picture entirely.

## The New Execution Stack

Here is how `await Post.objects.aget(id=1)` flows through Django 6.0:

```
await Post.objects.aget(id=1)
  └── QuerySet.aget()
        └── SQLCompiler.async_execute_sql()
              └── DatabaseWrapper.async_connection()   # ContextVar-scoped
                    └── psycopg.AsyncConnection
                          └── AsyncCursor.execute()
                                └── asyncio TCP socket write
                                └── await socket read   ← event loop released here
                                └── row data returned
```

And here is the same call under Django 5.x:

```
await Post.objects.aget(id=1)
  └── QuerySet.aget()
        └── sync_to_async(thread_sensitive=True)(QuerySet.get)
              └── ThreadPoolExecutor — OS thread blocked
                    └── SQLCompiler.execute_sql()
                          └── psycopg2 connection (thread-local)
                                └── libpq blocking TCP call
                                └── thread wakes, result returned
```

The event loop is no longer handing work off to a thread. It suspends the coroutine,
does other work, and resumes when the socket is readable. That is the entire reform,
and it is enough.

## What This Means For Concurrency

The practical payoff is in connection count. With the old thread approach, five hundred
concurrent async requests meant up to five hundred threads and up to five hundred
Postgres connections. Threads are cheap but not free — each costs roughly 8MB of stack
by default, plus scheduler overhead.

With native async, those same five hundred requests can be multiplexed over a
connection pool sized to what your database can actually handle, typically 10 to 50
connections, with the event loop running the wait queue. You use far fewer threads,
one or a handful for the event loop workers, and far fewer database connections.

Django 6.0 also ships native connection pooling for the async path[^3], built on
`psycopg_pool.AsyncConnectionPool`:

```python
# settings.py — async pooling in Django 6.0
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {
            "pool": {
                "min_size": 2,
                "max_size": 10,
            },
        },
        "CONN_MAX_AGE": 0,
    }
}
```

This is the same `pool` option I covered in [Cut Django Database Latency by 50-70ms With
Native Connection Pooling](/articles/2025/06/django-psycopg-native-pooling/), with one
difference that matters. In that post I warned against native pooling under ASGI —
Django's own docs recommended PgBouncer instead — because the sync pool and the event
loop did not cooperate. Django 6.0's `AsyncConnectionPool` is what closes that gap. The
pool itself is now async-aware, so the ASGI caveat no longer applies on the native
psycopg3 path. I was right to warn you then. You can stop worrying about it now.

## Is sync_to_async Gone?

No, and it should not be. It is the fallback for drivers that cannot go native async:

| Driver | Async path |
|---|---|
| psycopg3 (PostgreSQL) | Native `AsyncCursor` — no threads |
| psycopg2 (PostgreSQL) | `sync_to_async` thread wrap — still blocked |
| mysqlclient / MySQL | `sync_to_async` thread wrap |
| sqlite3 | `sync_to_async` thread wrap |

Run Django 6.0 against `psycopg2` or MySQL in an async context and Django still falls
back to the thread pool. The native path only exists when psycopg3 is installed and
configured. The thread trick did not become wrong. It became the path of last resort.

The way forward for other databases is psycopg3-equivalent async drivers. MySQL has
`aiomysql`, SQLite has `aiosqlite`. Django contributions for those backends are in
progress but not stable in 6.0, so for now PostgreSQL is the database that gets the
real thing.

## asyncpg Is Still Faster, And Still Not Supported

Benchmark `asyncpg` against psycopg3 on raw async throughput and asyncpg wins, often
by 20 to 40 percent on bulk read workloads. Django will not adopt it. The reasons are
structural, not political, and I think Django is right.

- **No DB-API2.** asyncpg uses positional `$1, $2` parameters, not `%s`. The entire
  ORM query compiler assumes `%s`.
- **No synchronous fallback.** Management commands, migrations, and sync views would
  need a whole separate code path.
- **A different transaction model.** asyncpg handles transactions differently from the
  DB-API2 autocommit and explicit model Django manages internally.

A faster driver that does not speak your ORM's contract is not a faster ORM. It is a
rewrite wearing a benchmark. If you genuinely need asyncpg throughput with a Django-like
ORM, look at SQLAlchemy 2.0 with its async session support and asyncpg backend, running
under Starlette or FastAPI. For Django, psycopg3 is the correct answer.

## Upgrading

To get the native async path today:

```bash
pip install "psycopg[binary,pool]"
```

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mydb",
        "USER": "myuser",
        "PASSWORD": "mypassword",
        "HOST": "localhost",
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "pool": True,  # or dict with min_size/max_size
        },
    }
}
```

If you are on Django 5.2 LTS with psycopg3, you already get the synchronous psycopg3
path and connection pooling. The native async query path needs Django 6.0. You can
upgrade the driver without upgrading Django and still get the pooling benefits in sync
contexts, which is a fine thing to do while you wait.

## Why It Took Five Years

Django's async ORM story ran from "fake async with threads" in 3.1 in 2020 to "native
async with psycopg3" in 6.0 in 2025. Five years sounds slow until you look at what had
to be true first:

1. `psycopg3` had to be stable enough to depend on, which it reached around 2022 to 2023.
2. Thread-local connection state was woven through the codebase, and the ContextVar
   migration touched hundreds of files.
3. The Django project is conservative about breaking changes, especially in database
   handling, where bugs are not cosmetic.

The result is correct and maintainable rather than the absolute fastest thing money can
buy, and I do not think that was the wrong trade. For most Django applications — web
services handling thousands of concurrent HTTP requests — native async with psycopg3 is
already more than fast enough, and it integrates cleanly with everything else in the
ecosystem.

## Related reading

- [Cut Django Database Latency by 50-70ms With Native Connection Pooling](./django-psycopg-native-pooling.md) — the sync side of the same story: configuring the psycopg3 pool, sizing `min_size`/`max_size`, and avoiding the `CONN_MAX_AGE` foot-gun.

[^1]: [PEP 249 — Python Database API Specification v2.0](https://peps.python.org/pep-0249/) — The DB-API2 spec that Django's ORM is built on top of; asyncpg deliberately does not implement it.
[^2]: [psycopg3 — Async operations](https://www.psycopg.org/psycopg3/docs/advanced/async.html) — Official psycopg documentation on the async connection and cursor API.
[^3]: [Django 6.0 Release Notes](https://docs.djangoproject.com/en/6.0/releases/6.0/) — Full changelog including async ORM changes, background tasks, and template partials.
