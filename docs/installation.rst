Installation
============

Installation should be easy as the following:

.. code:: 

   pip install git+git://github.com/jondoesntgit/willireply.git

If you experience any issues, please write about it in the `Github Issue Tracker <https://github.com/jondoesntgit/willireply/issues>`_

Otherwise, you should ensure that you've installed all of the libraries in `requirements.txt`

Setting Environment Variables
-----------------------------

You will need to copy ``.env.example`` into ``.env`` (which is hidden by .gitignore). Then you will need to fill in the location of the enron corpus on your hard drive (which should also not be checked into version control), as well as where you want to store the index of that corpus.

.. _download_enron:

Downloading the Enron Corpus
----------------------------

The `Enron dataset <https://www.cs.cmu.edu/~./enron/>`_ contains about 500,000 emails from about 150 users. The compressed archive is 432 Mb when zipped, 2.5 Gb when unzipped. It can be `downloaded here <https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz>`_, and should *not* be checked into version control. It should also probably not be kept in a cloud-synced service like Box or Dropbox. It's just too big.

You can download and unzip the Enron Corpus by running from the project root

.. code::

   make download
   make unzip

Generating PDFs
---------------

The PDFs and associated .log, .aux files are not included in this repository. They can be created by entering each report's specific directory (e.g. ``p-proposal``) and running :code:`latexmk -bibtex -pdf p-proposal`