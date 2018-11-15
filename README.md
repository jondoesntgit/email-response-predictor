# Will I Reply?

Project for Stanford's CS 221. Machine learning algorithm that predicts whether you'll respond to a given email.

Repo structure modeled after https://drivendata.github.io/cookiecutter-data-science/

## Installation

Ensure that you have installed all of the libraries in `requirements.txt`

You will need to copy `.env.example` into `.env` (which is hidden by .gitignore). Then you will need to fill in the location of the enron corpus on your hard drive (which should also not be checked into version control), as well as where you want to store the index of that corpus.

There are several files that are not included in this repository:

- The [Enron dataset](https://www.cs.cmu.edu/~./enron/) contains about 500,000 emails from about 150 users. The compressed archive is 432 Mb when zipped, 2.5 Gb when unzipped. It can be [downloaded here](https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz), and should *not* be checked into version control. It should also probably not be kept in a cloud-synced service like Box or Dropbox.
- The PDFs and associated .log, .aux files are not included in this repository. They can be created by entering each report's specific directory (e.g. `p-proposal`) and running `latexmk -bibtex -pdf p-proposal`

## Tagging for replies

In Gmail's format, each email has a "Reply-To-ID", which identifies what email (if any) this message is a response to. This allows us to run a single (albeit long) SQL query to look for messages whose id is in the "Reply-To-ID" column of another email.

In the Enron corpus, this is somewhat more challenging. An email is considered to have been replied to if there exists at least one email in that user's account such that all of the following are satisfied:

1. The email is in the sent folder
2. The email occurs after the first email
3. The subject line contains the original subject
4. The body of this email contains the original body

This method isn't complete, as some users would delete the original email. An alternative would be to go off of the subject alone, but there are many users who would use blank subject lines.
