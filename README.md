# Quickly start with `aiophoenixdb`
## What is `aiophoenixdb`
This project is based on the Apache Software Foundation open source project Apache-Phoenixdb project to transform</br>
 the call implementation of the Avatica protocol in the code from the original synchronous mode to asynchronous call.
## How to install
Pypi page: [aiophoenixdb](https://pypi.org/project/aiophoenixdb/)
```shell
pip install aiophoenixdb
```
## How to use

- Query sample
```python
import aiophoenixdb
import asyncio

PHOENIX_CONFIG = {
    'url': 'http://xxxxxxxxxx',
    'user': 'xxx',
    'password': 'xxx',
    'database': 'xxx'
}

async def query_test():
    conn = await aiophoenixdb.connect(**PHOENIX_CONFIG)
    async with conn:
        async with conn.cursor() as ps:
            # need await
            await ps.execute("SELECT * FROM xxx WHERE id = ?",  parameters=("1", ))
            res = await ps.fetchone()
            print(res)

# Throw the query coroutine into the event loop to run
asyncio.get_event_loop().run_until_complete(query_test())
```

- Query with DictCursor

```python
import aiophoenixdb
import asyncio
from aiophoenixdb.cursors import DictCursor

PHOENIX_CONFIG = {
    'url': 'http://xxxxxxxxxx',
    'user': 'xxx',
    'password': 'xxx',
    'database': 'xxx'
}

async def query_test():
    conn = await aiophoenixdb.connect(**PHOENIX_CONFIG)
    async with conn:
        async with conn.cursor(cursor_factory=DictCursor) as ps:
            # need await
            await ps.execute("SELECT * FROM xxx WHERE id = ?",  parameters=("1", ))
            res = await ps.fetchone()
            print(res)

# Throw the query coroutine into the event loop to run
asyncio.get_event_loop().run_until_complete(query_test())
```

## Performance
### Compare with `phoenixdb`
#### phoenixdb
```python

```

#### aiophoenixdb
```python

```
