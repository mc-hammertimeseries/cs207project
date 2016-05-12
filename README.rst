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
Write about the REST API here.

Cython-Wrapped FFTW
===================
For our extra feature, we wrapped FFTW in Cython for fast calculation of cross-correlation. To compute a discrete Fourier transform using FFTW, you first allocate memory for the input and output and create an ``fftw_plan`` variable specifying how long the input is whether you want to do a forward or inverse transform. You then copy the desired input into the allocated input memory and execute the plan, leaving the result in the output memory. Finally, you free all the memory you allocated and destroy the plan. We wrote a Cython package that allows the calling function to leverage FFTW's speed without dealing with its complexity.

We decided to implement the cross-correlation as a callable function rather than as a class. This requires some sacrifices; for example, we can no longer allocate one plan and call it multiple times. However, we pass the flag ``FFTW_ESTIMATE`` when creating plans, which significantly speeds up plan creation at the expense of execution time. This tradeoff makes all cross-correlation queries reasonably fast and avoids the problem of having an extremely slow query during which the plan is set up. Furthermore, there is no guarantee that all time series in our database would be of the same length, so the time spent saving a plan could be wasted. Perhaps, in a more advanced version of our database, an advanced user who knew the sort of queries they would be making could choose which type of plan to create.
