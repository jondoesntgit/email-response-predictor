Working with a Personal GMail Account
=====================================

Downloading emails
------------------

There's still a little bit more work to be done here, but as a first pass, if you want to download a bunch of your recent GMails, that can be done by merely running

.. code::

   python willireply/data/gmail.py

This will take your emails and drop them into ``data/raw``, and will also create an index of these emails in ``data.sqlite3``. In order for this to work, you must have put your GMail username and password in the ``.env`` file in your project root as ``WILLIREPLY_EMAIL`` and ``WILLIREPLY_PASSWORD``. 

Labeling
--------

In Gmail's format, each email has a "Reply-To-ID", which identifies what email (if any) this message is a response to. This allows us to run a single (albeit long) SQL query to look for messages whose id is in the "Reply-To-ID" column of another email.