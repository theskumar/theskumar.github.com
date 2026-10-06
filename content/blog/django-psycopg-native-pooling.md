+++
title = "Django Native PostgreSQL Connection Pooling"
date = "2025-06-18"
description = "Configure Django’s native PostgreSQL connection pool with psycopg, handle connection cleanup, and measure performance before and after."
tags = [
    "django",
    "postgresql",
    "performance",
    "python"
]
+++

Opening PostgreSQL connections adds overhead. Django 5.1 (released August 7, 2024) added native connection pooling[^1], which lets an application reuse connections. Measure connection overhead and response times before and after enabling it; the benefit depends on your workload.

> If you're on Django 6+ and running async/ASGI, also see the async pool notes in [How Django's ORM Went From
> sync_to_async Threads to Native
> psycopg3](./django-async-orm-deep-dive.md).

## Native Pooling vs External Pooling

PgBouncer runs as a separate pooling server. Django’s native pooling runs in the application process, so it does not require a separate server. It does require psycopg’s pool package. Third-party Django pooling packages and manual connection management are other options, with their own maintenance and configuration needs.

## Configure Native Pooling

**Requirements**: Django 5.1+ and PostgreSQL (this feature does not work with
psycopg2)[^2]

Install the correct package:

```bash
pip install "psycopg[binary,pool]"
```

**Critical**: The package is called `psycopg` (not `psycopg3`). The pool
functionality requires a separate package that this command installs
automatically[^3].

Add these lines to your `settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "your_db_name",
        "USER": "your_db_user",
        "PASSWORD": "your_db_password",
        "HOST": "your_db_host",
        "PORT": "5432",
        "CONN_MAX_AGE": 0,  # Required - pooling fails without this
        "OPTIONS": {
            "pool": True,
        },
    }
}
```

Deploy this change. Your app now reuses connections instead of creating new ones
for every request.

## Prevent the Configuration Error That Breaks Production

**Must set `CONN_MAX_AGE = 0`**. Without this, Django throws
`ImproperlyConfigured: Pooling doesn't support persistent connections` and your
app crashes[^4]. The pool manages connection lifetimes, making Django's
persistence redundant.

## Scale for High-Traffic Production

Replace `"pool": True` with specific parameters for production loads:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "your_db_name",
        "USER": "your_db_user",
        "PASSWORD": "your_db_password",
        "HOST": "your_db_host",
        "PORT": "5432",
        "CONN_MAX_AGE": 0,
        "OPTIONS": {
            "pool": {
                "min_size": 4,         # Keeps connections warm
                "max_size": 16,        # Handles traffic spikes
                "timeout": 10,         # Fails fast under extreme load
                "max_lifetime": 1800,  # 30 minutes maximum connection age
                "max_idle": 300,       # Close idle connections after 5 minutes
            },
        },
    }
}
```

Start with `max_size` equal to expected concurrent users divided by 10. Scale up
if you see timeout errors in logs.

## Monitor Your Performance Gains

Enable pool monitoring to track your improvements:

```python
# In settings.py
import logging
logging.getLogger('psycopg.pool').setLevel(logging.INFO)
```

Watch pool utilization, connection wait times, timeout errors, and response times. Record median and 95th percentile latency before and after the change under comparable load. Use those measurements to size the pool and judge whether pooling helps your application.

## Critical Fix for Threading and Celery Applications

**Essential for background processing**: This isn't a pooling bug — it's expected
Django behavior that pooling simply makes painful. Any connection opened outside
Django's request-response cycle (for example, in a thread you spawn yourself)
stays open until you explicitly close it. Without a pool you might not notice;
with one, those un-returned connections exhaust `max_size` and you start seeing
`PoolTimeout` errors[^5]. Add explicit cleanup:

```python
from django.db import connection
from threading import Thread

class DataProcessingThread(Thread):
    def run(self):
        # Your database operations here
        User.objects.filter(active=True).update(last_seen=timezone.now())

        # Critical: returns the connection to the pool
        connection.close()
```

For code that may touch multiple database aliases, Django's documented helper
`django.db.close_old_connections()` is the more robust choice — it closes all
old or unusable connections across every configured database:

```python
from django.db import close_old_connections

class DataProcessingThread(Thread):
    def run(self):
        try:
            User.objects.filter(active=True).update(last_seen=timezone.now())
        finally:
            close_old_connections()
```

Without this cleanup, each background thread permanently holds a connection from
your pool.

## Deployment Scenarios That Require Different Approaches

**ASGI applications**: On Django 5.1–5.2, Django's documentation recommends
against native pooling with ASGI — use PgBouncer or similar external poolers
instead. This changed in Django 6.0, which ships an async-aware
`AsyncConnectionPool` that works correctly under ASGI. I cover how that fits
together with the truly-async ORM in [How Django's ORM Went From sync_to_async
Threads to Native psycopg3](/articles/2026/06/django-orm-from-sync_to_async-threads-to-native-psycopg3/).

**Serverless deployments**: Connection pools don't persist across serverless
invocations. Skip this optimization for Lambda/Cloud Functions.

**Multi-tenant applications**: Each tenant database needs its own pool
configuration in `DATABASES`.

## When to Evaluate Pooling

Evaluate pooling when connection establishment is a measurable part of request latency, concurrency is growing, or the application is approaching PostgreSQL connection limits. Compare measurements before and after rather than assuming a fixed latency or cost saving.

[^1]: [Django 5.1 Release Notes](https://docs.djangoproject.com/en/5.1/releases/5.1/) - Official Django documentation announcing native connection pooling support
[^2]: [Django Database Configuration](https://docs.djangoproject.com/en/5.2/ref/databases/) - Complete guide to Django database settings including pooling requirements
[^3]: [psycopg Installation Guide](https://www.psycopg.org/psycopg3/docs/basic/install.html) - Official psycopg documentation for package installation and pool dependencies
[^4]: [Stack Overflow: Django Pooling Configuration Error](https://stackoverflow.com/questions/78879329/django-improperlyconfigured-pooling-doesnt-support-persistent-connections) - Community discussion of the CONN_MAX_AGE requirement
[^5]: [Django Ticket #35672](https://code.djangoproject.com/ticket/35672) - Closed as *invalid*: connections opened in threads must be returned manually. See also the [Databases → Caveats](https://docs.djangoproject.com/en/stable/ref/databases/#caveats) docs, which recommend `django.db.close_old_connections()` for connections created outside the request-response cycle.
