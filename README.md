# Spout
Spout is a method of enterprise and beta distribution of iOS and Android apps.  It is written in Python and uses
the Django web framework.

## Installation

First, instantiate a virtualenv (http://pypi.python.org/pypi/virtualenv) on the Spout directory.
All dependencies are included in this repo under the requirements.txt file.  Run pip install -r requirements.txt
to get the dependencies needed.  You then can configure the app just like you would any other Django app.

## Local Development

If you are going to use Sqlite3 for your local development database, be sure to run `pip install pysqlite`.  
Otherwise you may get a rather cryptic error stating that Django cannot load one of its components (because loading the database engine didn't work),
though no helpful error message is shown.
