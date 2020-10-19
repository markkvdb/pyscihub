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

Installing the Sci-Hub CLI is as easy as cloning this repo and installing it using pip, i.e.,

.. code-block:: bash

    git clone https://github.com/markkvdb/pyscihub.git
    cd pyscihub
    pip install -e .

If you don't want to change the standard output folder, then make sure that you create a `output` folder in the `pyscihub` folder.

Usage
--------

Tool can be used with a single query, e.g.,

.. code-block:: bash

    pyscihub single "Your paper"

or with a user-provided file containing one query per line as

.. code-block:: bash

    pyscihub file <LOCATION FILE>

If everything goes well, a file `output/pdf_paths.csv` is created containing the location of the PDFs of all requested queries. If Sci-Hub cannot find the corresponding PDF then the field is empty.
