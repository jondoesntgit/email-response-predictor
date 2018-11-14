# Will I Reply?

Project for Stanford's CS 221. Machine learning algorithm that predicts whether you'll respond to a given email.

Repo structure modeled after https://drivendata.github.io/cookiecutter-data-science/

## Installation

There are several files that are not included in this repository:

- The [Enron dataset](https://www.cs.cmu.edu/~./enron/) contains about 500,000 emails from about 150 users. The compressed archive is 432 Mb when zipped, 2.5 Gb when unzipped. It can be [downloaded here](https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz), and should *not* be checked into version control. It should also probably not be kept in a cloud-synced service like Box or Dropbox.
- The PDFs and associated .log, .aux files are not included in this repository. They can be created by entering each report's specific directory (e.g. `p-proposal`) and running `latexmk -bibtex -pdf p-proposal`