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


Installation
--------

Installing the Sci-Hub CLI is easiest using pip as

.. code-block:: bash

    pip install -e .

Usage
--------

Tool can be used with a single query, e.g.,

.. code-block:: bash

    pyscihub single "Your paper"

or with a user-provided file containing one query per line as

.. code-block:: bash

    pyscihub file demo.txt
