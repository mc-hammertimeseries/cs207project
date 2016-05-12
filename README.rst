=========================
CS207 Time Series Project
=========================
A package for storing and manipulating time series.

``timeseries``: Code for creating and manipulating time series

``pype``: A domain-specific language for time series analysis.

``tsdb``: A database for storing, searching, and manipulating time series.

``procs``: Procedures that can be executed on time series stored in the database.

``fft``: Cython-wrapped ``fftw`` for fast cross-correlation.

``tests``: Tests for other modules.

.. image:: https://travis-ci.org/mc-hammertimeseries/cs207project.svg?branch=master
   :target: https://travis-ci.org/mc-hammertimeseries/cs207project

.. image:: https://coveralls.io/repos/github/mc-hammertimeseries/cs207project/badge.svg?branch=master 
   :target: https://coveralls.io/github/mc-hammertimeseries/cs207project?branch=master

Installation
------------
text text text

The files needed to build Cython FFT module for computing cross-correlation from scratch (``fft.pyx``, ``cfft.pxd``, ``fft_defs.h``, ``setup.py``) are included, along with the generated ``fft.c`` and ``fft.so`` files. If it works on your system, the easiest option is to just use the ``fft.so`` file. Otherwise, you must install version 3.3.4 of `FFTW <http://www.fftw.org/>`_ and compile the Cython files manually. This can be done by running::

    python setup.py build_ext --inplace

from ``/procs/fft/``.


Persistence, REST API, and Cython-Wrapped FFTW
----------------------------------------------

Persistence
===========
In our database, time series are each stored in separate files called ``ts{i}.json``, where ``{i}`` is replaced by the primary key. We also have one pickled index file ``indices.pkl`` that stores data structures for all secondary indices. For example, one part of ``indices.pkl`` storing the secondary index for ``order`` might look like

    ``'order': {B+-tree}``

where ``{B+-tree}`` is a B+-tree whose nodes are lists of primary keys with the given value of ``order``.

To make our database persistent, we store both a local copy of our database and a copy on disk. When a commit occurs, the local copy is written to disk. If a rollback occurs, the disk copy is written locally. Time series files that are scheduled for deletion are given the extension ``.trash``, and when a commit happens, all files with that extension are deleted. In the event of a rollback, the extension is removed.

REST API
========
We implemented a rest API using Tornado. In many of the routes the following parameterization is used:

**metadata_dict**:

+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Query Parameter | Description                                                                                                                                                 |
+=================+=============================================================================================================================================================+
| field(i)        | Name of field                                                                                                                                               |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
| value(i)        | Value of field                                                                                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
| from(i)         | Value field must be greater than or equal to, assumes field numeric type                                                                                    |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
| to(i)           | Value field must be less than or equal to, assumes field numeric type                                                                                       |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+
| dtype(i)        | Optional argument given with value(i), can be one of int, float or bool. Bool implies true/false or 1/0 value. If no value given assumes field is a string. |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------+

where (i) represents an ordered index starting from 1, e.g. field1=pk&value1=ts1&field2=order&from2=1&to2=5

**additional_params**:

+-----------------------+---------------------------------------------------------------------------+
| Query Parameter       | Description                                                               |
+=======================+===========================================================================+
| sort_by               | Name of field to sort by                                                  |
+-----------------------+---------------------------------------------------------------------------+
| sort_by_increasing    | true/false or 1/0 to indicate increasing or decreasing order respectively |
+-----------------------+---------------------------------------------------------------------------+
| limit                 | Integer argument for number of results returned                           |
+-----------------------+---------------------------------------------------------------------------+

e.g. sort_by=order&sort_by_increasing=true&limit=10

+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| Route                      | Method | Description                                      | Parameters                                                                                                                         | Example (Using Python's requests package)                                                                                   |
+============================+========+==================================================+====================================================================================================================================+=============================================================================================================================+
| /api/timeseries            | POST   | Insert a timeseries                              | json body with fields pk, t, v corresponding to primary key (string), times (array), and values (array)                            | requests.post("http://localhost:5000/api/timeseries", json = {'t':list(range(1,10)), 'v':list(range(101,110)), 'pk':"1"})   |
+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| /api/timeseries            | GET    | Select timeseries                                | metadata_dict, additional_params, optional fields parameter to specify what to return (default returns all fields)                 | requests.get("http://localhost:5000/api/timeseries?field1=pk&value1=1&fields=blarg&fields=order")                           |
+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| /api/timeseries            | DELETE | Delete timeseries                                | pk argument for timeseries                                                                                                         | requests.delete("http://localhost:5000/api/timeseries?pk=1")                                                                |
+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| /api/timeseries/upsert     | POST   | Upsert data into a timeseries                    | json body with field pk and data to upsert                                                                                         | requests.post("http://localhost:5000/api/timeseries/upsert", json = {'pk':"1", 'blarg':123, 'order':1})                     |
+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| /api/timeseries/augmented  | GET    | Augmented select for a timeseries                | proc: name of procedure, target: fields to put results in, arg: any argument for the procedure, metadata_dict, additional_params   | requests.get("http://localhost:5000/api/timeseries/augmented?proc=stats&target=mean&target=std&field1=pk&value1=1")         |
+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+
| /api/timeseries/similarity | GET    | Calculate similarity of timeseries to chosen pks | pk(i) for i=1..5 indicating vantages points for d_vp-i, metadata_dict, additional_params                                           | requests.get("http://localhost:5000/api/timeseries/similarity?pk1=1&pk2=2&sort_by=d_vp-1&limit=2")                          |
+----------------------------+--------+--------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------+

Cython-Wrapped FFTW
===================
For our extra feature, we wrapped FFTW in Cython for fast calculation of cross-correlation. To compute a discrete Fourier transform using FFTW, you first allocate memory for the input and output and create an ``fftw_plan`` variable specifying how long the input is whether you want to do a forward or inverse transform. You then copy the desired input into the allocated input memory and execute the plan, leaving the result in the output memory. Finally, you free all the memory you allocated and destroy the plan. We wrote a Cython package that allows the calling function to leverage FFTW's speed without dealing with its complexity.

We decided to implement the cross-correlation as a callable function rather than as a class. This requires some sacrifices; for example, we can no longer allocate one plan and call it multiple times. However, we pass the flag ``FFTW_ESTIMATE`` when creating plans, which significantly speeds up plan creation at the expense of execution time. This tradeoff makes all cross-correlation queries reasonably fast and avoids the problem of having an extremely slow query during which the plan is set up. Furthermore, there is no guarantee that all time series in our database would be of the same length, so the time spent saving a plan could be wasted. Perhaps, in a more advanced version of our database, an advanced user who knew the sort of queries they would be making could choose which type of plan to create.
