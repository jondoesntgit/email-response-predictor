Comparing Models
================

There are several different models which we consider in this project. We did our best to do an apples-to-apples comparison of each model. We also invested effort towards automating each step of the machine-learning process.

Splitting Data into Training/Validation and Test Sets
-----------------------------------------------------

For an apples-to-apples comparison, each model should train on the same training set, and test on the same test set. Rather than randomly shuffle the data each time a model is run, the test sets are built once, and then stored on the hard drive.

For memory efficiency, only the indices of the email files in the sqlite3 database are stored in this table. It is stored as ``split.json`` at the location specified by ``SPLIT_FILE`` in your ``.env`` file. 

For computational efficiency (at the cost of memory), the training set is cached in a sibling file to ``split.json`` as ``validation_set.pkl``. It is a pickled DataFrame that contains only the user, the subject, and the filename of each email.

These scripts can be run using

.. code::

   make datasets

Building the Feature Vectors
----------------------------

Due to the size and richness of the datasets, the feature vectors take some time to compute. In order to save computing resources, when the ``FeatureExtractor``s are defined, they are serialied in the ``FEATURE_EXTRACTOR_DIRECTORY``. This process only takes a few seconds.

Next, the feature extractors convert emails into feature vectors. Depending on the complexity of the feature extractor, this process takes many minutes per feature vector, and the resulting data consumes a lot of memory on the disk. Be patient. Processed feature vectors are stored in ``PROCESSED_DATA_DIRECTORY`` as numpy files.

These scripts can be run using

.. code:: 

   make features

Training Models
---------------

Each model is an implementation of a ``BaseModel`` abstract class. Each implementation of ``BaseModel`` should implement these functions

- ``__init__(name)`` - to initialize the model, at which time the default ``name`` value is set
- ``train(x, y)`` - to train using training data and labels
- ``predict(x)`` - return a ``y`` based on ``x``. Used in the testing phase

Additionally, ``BaseModel`` comes with a the following functions

- ``test(x, y)`` - Uses the ``predict`` function to predict y values, and compares them against the true labels. At this time, the function generates a report, and stores it in the folder determined by your ``.env`` file's ``RESEULTS_DIRECTORY``
- ``serialize()`` - Serializes the trained model into the ``RESULTS_DIRECTORY``.

All of the models can be trained and tested with this code:

.. code::

   make models


Visualizing the Results
-----------------------

The performance of each model is kept in an html file that is kept in a directory defined by the ``RESULTS_DIRECTORY`` setting in your ``.env`` file.

To quickly open all of these files as separate tabs in your default web browser, run

.. code::

   make visualize

