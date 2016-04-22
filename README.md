# TSDB Part 3 (Part of Milestone 2)

This is a skeleton for the database part of milestone 2 of your project.

## What does this version add?

- selects now have a dictionary argument "additional" which adds sorting and limits
- selects now use OrderedDicts, since `additional` now allows for sort orders. Last time we wrote things that only Dicts were sent back. Now we want to preserve order. check `deserialize to see how this survives JSON`. To see how OrderedDicts are used check out `_select` in `tsdb_server.py`.
- augmented selects which are like triggers but run synchronously after a
select and send back their results
- correlation distances machinery to implement vantage point based searching in `corr.py` and `_corr.py` in procs
- an implementation of nearest neighbor search using two augmented selects to the same proc but with different arguments.

## copying this over

You want to copy `both.sh` and the `go-*` files to the toplevel of your project, and the subfolder `tsdb` to be at par with the rest of your project modules such as `timeseries` and `pype`.

## running the client and server

- You can run both the client and the server to (informally) test your output together as `sh both.sh` from this folder.
- `go_server.py` sets up the database schema and the database server. THE SCHEMA HAS CHANGED from master
- `go_client.py` has a set of commands to run from the client to the server, inserting some time-series (`insert_ts`), updating if not inserting and inserting otherwise their metadata (`upsert_meta`), and carrying out a select `select`. THERE IS MORE
COMMANDS IN THERE NOW

## whats new?
- the schema has changed in `go_server.py` to add a boolean about if a given time-series is a vantage point or not.
- there are changes in `go_client.py` to add more client calls. You must also implement code there which will do a nearest neighbor search in time series using the algorithm pavlos described in class.
- there is an `augmented_select` method. See the procs folder in the repo. Augmented procs are defined there, as `proc_main`. In `corr.py` we have a `proc_main` function and a `main` coroutine. The name of the augmented-select proc is the name of the module; the coroutine itself must be called `proc_main`.
- you must provide a client side implementation of augmented select. The server implementation is provided for you in `tsdb_server.py`.
- select has changed by adding `additional`. See the spec in tsdb_ops and the comments in `dictdb.py`. The server wrapper
around the dictdb's select is provided in `tsdb_server.py`, you must write both the dictdb implementation and the select client in `tsdb_client.py`.
- selects now use OrderedDicts. This is done for you in `tsdb_server.py`

## additional specs for `select` and `augmented_select`

- procs return an array of their results (just like triggers). You can return None as one of these results. The targets are sent back as  keys paired with values from the procs as the synchronous result of an augmented select

- `select` takes a `metadata_dict` and `fields`.
    - `additional` is a dictionary. It has two possible keys:
    (a){'sort_by':'-order'} or {'sort_by':'+order'} where order
    must be in the schema AND have an index. (b) limit: {'limit':10}
    which will give you the top 10 in the current sort order.
    - `_select` in `tsdb_server.py` and `deserialize` in `tsdb_serialization.py` show you how OrderedDicts are used.


## the `tsdb` module: here is where you do the work.

Signatures for all the implementations you need to do are provided to you in the files themselves. A transcript of the output this time around can be seen in [output3.md](output3.md).

- `__init__.py` exports the module
- `dictdb.py` **implements an in-memory, dictionary based database**. You will be implementing large chunks of this. NEW WORK TO BE DONE HERE. select HAS
CHANGED. See below for how.
- `tsdb_client.py` **implements a client for the database that packs the json and sends it out**. You will be implementing all of this. You are free to do this using asyncio or synchronous socket techniques. Keep in mind that you might want to reuse these functions inside a http server which you will be writing for the end of your project: if you want to implement this server synchronously in flask for example, you might want to use synchronous technology. On the other hand if you want to use `aiohttp` or `tornado`, use something asynchronous and figure out how to combine both the http serving and the database client calls in the same event loop. NEW WORK TO BE DONE HERE, for `select` and `augmented_select`.
- `tsdb_server.py`: ** unpack json and run **: currently, at least, we provide all the implementation of a callbacks based asynchronous socket server. Please read carefully how this file works as we will ask you to make modifications to it later next week.
- `tsdb_error.py`: **provides error and status handling**
- `tsdb_ops.py`: **documents the database ops supported**, including their "string names" in the `typemap`, and **conversion to and from a json-like dictionary structure**
- `tsdb_serialization.py`: in class you saw how client-server communication benefits from having some **wire format**. Here you will implement the serialization from json-like dictionary, to json, to bytes on the network. We implement de-serialization for you. NO WORK HERE THIS TIME

## Additional work besides that in `tsdb` module

- make sure you check changes to the schema in `go_server.py`
- you must implement code towards the end of `go_client.py` to implement time series similarity search in two augmented selects
- for this see `procs/corr.py`. That imports `procs/_corr.py` where you must provide the core code for the similarity search based on Pavlos's lecture and the lab that day.
- you must test and robustify all code you write in the client and dictdb.py. Additionally, robustify and test code in `tsdb_server.py`. While you wont be graded on that for milestone 2, you WILL be on your overall project. So might as well get it early. The reference implementation provided by us has almost no error checking. An error scheme is in `tsdb_error.py` and is marginally used. You should use it, and may even want to augment in in some cases.
