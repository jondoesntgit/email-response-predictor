Woring with SQLite3
===================

We chose to use SQLite3 databases to index the emails that we worked with. They're SQL databases contained within a single, portable file. By convention, we chose to index only one user's email in a SQLite3 file. Otherwise, the files get rather large. Breaking them into individual files makes working with different users a bit more modular.


Basic SQLite3 queries
---------------------

To inspect a file, open it using the shell program of the same name

.. code:: sql

   $ sqlite3 ~/Documents/enron/indices/allen-p.sqlite3

   sqlite> SELECT id, subject, reply_id FROM emails WHERE did_reply=1 LIMIT 10;
    21|Final FIled Version|1306
    28|Re:|1425
    36|Enron Response to San Diego Request for Gas Price Caps|1773
    37|New Generation, Nov 30th|1710
    54|Check this out -|907
    70|Summary of Today's Meeting|977
    79|Bishops Corner|1132
    100|RE: Distribution Form|951
    105|Answer|1221
    149|Additional properties in San Antonio|1198

   sqlite> -- more commands
   sqlite> .exit
   $ 


Python and SQLite3
------------------

These SQL queries can be run in Python like this:

.. code:: python

   import sqlite3

   query = '''
   SELECT id, subject, reply_id 
   FROM emails 
   WHERE did_reply=1 
   LIMIT 10;
   '''

   conn = sqlite3.connect(filename)
   c = conn.cursor()

   c.execute(query)
   for (id, subject, reply_id) in c:
       # do something
       pass


Or, if you prefer Pandas:

.. code:: python

  import sqlite3
  import pandas as pd
  conn = sqlite3.connect(filename)
  df = pd.read_sql_query('SELECT * FROM emails', conn)