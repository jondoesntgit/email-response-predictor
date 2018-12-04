Working with the Enron Corpus
=============================

The Enron corpus is a massive dataset comprised of 500,000 emails from 150 different users. It is too large to be included in this repo, but it can be downloaded several places on the web. Refer to :ref:`download_enron` for more information.

Indexing
--------

In the Enron corpus, this is somewhat more challenging. An email is considered to have been replied to if there exists at least one email in that user's account such that all of the following are satisfied:

1. The email is in the sent folder
2. The email occurs after the first email
3. The subject line contains the original subject
4. The body of this email contains the original body

This method isn't complete, as some users would delete the original email. An alternative would be to go off of the subject alone, but there are many users who would use blank subject lines.

To index all users

.. code:: python

   >>> from willireply.data import enron
   >>> enron.index()
   >>> enron.label()

You may find that this takes a significant amount of time (several hours). If you want to start with a single user, you can run

.. code:: python

   >>> from willireply.data import enron
   >>> enron.index('allen-p')
   >>> enron.is_labeled('allen-p')
   False
   >>> enron.label('allen-p')
   >>> enron.is_labeled('allen-p')
   True

