# TSDB Part 2 (Part of Milestone 2)

This is a skeleton for the database part of milestone 2 of your project.

## What does this version add?

- selects with predicates and choices of fields to return
-triggers (adding them, removing them, running them)

## copying this over

You want to copy `both.sh` and the `go-*` files to the toplevel of your project, and the subfolder `tsdb` to be at par with the rest of your project modules such as `timeseries` and `pype`.

## running the client and server

- You can run both the client and the server to (informally) test your output together as `sh both.sh` from this folder.
- `go_server.py` sets up the database schema and the database server. THE SCHEMA HAS CHANGED from master
- `go_client.py` has a set of commands to run from the client to the server, inserting some time-series (`insert_ts`), updating if not inserting and inserting otherwise their metadata (`upsert_meta`), and carrying out a select `select`. THERE IS MORE
COMMANDS IN THERE NOW

## whats new?
- the schema has changed in `go_server.py` to add a mean and a standard deviation
- there are changes in `go_client.py` to add more client calls.
- there is an `add_trigger` method. See the procs folder in the repo. You need to copy it at the same level as the tsdb folder. This is where you define triggers as coroutines. (you can use old style generators as well) We have provided some examples which you will need for this part of the project. The name of the trigger is the name of the module; the coroutine itself must be called `main`.
- there is also a `remove_trigger`. Server side implementations of both add and remove triggers are provided. You need to provide the client implementations as before. See `tsdb_ops` for the spec
- select has changed. See the spec in tsdb_ops andthe comments in `dictdb.py`. The server wrapper
around the dictdb's select is provided in `tsdb_server.py`, you must write both the dictdb implementation and the select client in `tsdb_client.py`.

## specs for `select` and `add_trigger` and `remove_trigger`

- coroutines return an array of their results. You can return None as one of these results but then make sure that target is None for that trigger.

- `add_trigger`: takes arguments
    - `proc`: name of module in procs with coroutine `main`,
    - `onwhat`: which op is this trigger running on, for example `"insert_ts"`,
    - `target`: an array of fieldnames (which must be in the spec) which will be mapped to the array of results from the coroutine. If the target is `None` rather than a list of fields, we'll assume no upserting. (see `tsdb_server.py` for the implementation.)
    - `arg`: an extra argument which you might pass in. We will use this later.

- `remove_trigger` takes `proc` and `onwhat` and removes all such triggers even if they have different targets and args.

- `select` takes a `metadata_dict` and `fields`.
    - the `metadata_dict` looks like this..`{'blarg': {'>=': 2}, 'order': 1}`. The `order` select is precise value,and you did this last time. The `blarg` can have multiple ops in the dictionary and implements range queries. You need to implement these in `dictdb.py`. Look at the `OPMAP` there for the ops needed. The ops are inefficient in two ways: (a) currently it is fine for you to do a FULL linear index scan per op (b) only binary ops are allowed, so a range is not explicitly coded.
    - `fields` can be `None` in which case we send back just the primary keys. If its an empty list, we send back all fields except the `ts` field. Otherwise you can explicitly code the fields. The format is given in `dictdb.py`:

    ```python
    # if fields is None: return only pks
    # like so [pk1,pk2],[{},{}]
    # if fields is [], this means all fields
    #except for the 'ts' field. Looks like
    #['pk1',...],[{'f1':v1, 'f2':v2},...]
    # if the names of fields are given in the list, include only those fields. `ts` ia an
    #acceptable field and can be used to just return time series.
    #see tsdb_server to see how this return
    #value is used
    ```

## the `tsdb` module: here is where you do the work.

Signatures for all the implementations you need to do are provided to you in the files themselves. A transcript of the output can be seen in [output2.md](output2.md).

- `__init__.py` exports the module
- `dictdb.py` **implements an in-memory, dictionary based database**. You will be implementing large chunks of this. NEW WORK TO BE DONE HERE. select HAS
CHANGED. See below for how.
- `tsdb_client.py` **implements a client for the database that packs the json and sends it out**. You will be implementing all of this. You are free to do this using asyncio or synchronous socket techniques. Keep in mind that you might want to reuse these functions inside a http server which you will be writing for the end of your project: if you want to implement this server synchronously in flask for example, you might want to use synchronous technology. On the other hand if you want to use `aiohttp` or `tornado`, use something asynchronous and figure out how to combine both the http serving and the database client calls in the same event loop. NEW WORK TO BE DONE HERE, for select as well as for the triggers.
- `tsdb_server.py`: ** unpack json and run **: currently, at least, we provide all the implementation of a callbacks based asynchronous socket server. Please read carefully how this file works as we will ask you to make modifications to it later next week.
- `tsdb_error.py`: **provides error and status handling**
- `tsdb_ops.py`: **documents the database ops supported**, including their "string names" in the `typemap`, and **conversion to and from a json-like dictionary structure**
- `tsdb_serialization.py`: in class you saw how client-server communication benefits from having some **wire format**. Here you will implement the serialization from json-like dictionary, to json, to bytes on the network. We implement de-serialization for you. NO WORK HERE THIS TIME

## How the database works

`dictdb` is a very simple (for-now) in memory database. No persistence.

- the primary key, which must be unique, is called `pk`
- `self.rows` contains all the rows. This is a dictionary with keys the primary keys
- `self.index` is a dictionary. The keys are the indexed fields. The values are the index for each field.
- The index itself is an inverse-lookup dictionary. Say a field `f` has values 1,9,33,1 in pks 1,2,3,4. Then self.index['f']={1:[1,4], 2:[9], 3:[33]}.
- Notice that we `update_indices` on all database changing operations. Here these are `insert_ts` and `upsert_meta`. You must implement the latter. You must also implement the `select` function.
