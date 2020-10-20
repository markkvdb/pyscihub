========
pyscihub
========


.. image:: https://img.shields.io/pypi/v/pyscihub.svg
        :target: https://pypi.python.org/pypi/pyscihub

.. image:: https://img.shields.io/travis/markkvdb/pyscihub.svg
        :target: https://travis-ci.com/markkvdb/pyscihub

.. image:: https://readthedocs.org/projects/pyscihub/badge/?version=latest
        :target: https://pyscihub.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Command-line and Python API to download PDFs directly from Sci-Hub


* Free software: MIT license
* Documentation: https://pyscihub.readthedocs.io.

Features

* Download 1,000s of academic articles without an academic account in one command
* Add new articles to the list without downloading existing articles twice
* Save important time looking up and downloading articles

Installation
------------------

To install pyscihub, run this command in your terminal:

.. code-block:: console

    $ pip install pyscihub

This is the preferred method to install pyscihub, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Usage
------------------

Tool can be used with a single query, e.g.,

.. code-block:: console

    $ pyscihub single "Your paper"

or with a user-provided file containing one query per line as

.. code-block:: console

    $ pyscihub file <LOCATION FILE>

If everything goes well, a file ``output/pdf_paths.csv`` is created containing the location of the PDFs of all requested queries. If Sci-Hub cannot find the corresponding PDF then the field is empty.
