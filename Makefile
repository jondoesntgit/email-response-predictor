#!make

include .env
export $(shell sed 's/=.*//' .env)


download:
	mkdir -p `dirname $(ENRON_DOWNLOAD_LOCATION)`
	curl -o $(ENRON_DOWNLOAD_LOCATION) https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tar.gz 

unzip:
	mkdir -p `dirname $(ENRON_FOLDER)
	tar --strip-components=2 -xvzf $(ENRON_DOWNLOAD_LOCATION) maildir/ --directory $(ENRON_FOLDER2)

index:
	mkdir -p $(ENRON_INDEX_FOLDER)
	# Technically this labels it as well
	python willireply/data/enron.py

datasets: # TODO: Depends on index enron
	python willireply/data/split_datasets.py

feature_extractors:
	python willireply/features/make_feature_extractors.py

features: # TODO: depends on split_enron_data and create_feature_extractors
	python willireply/features/extract_features.py

models:
	mkdir -p `dirname $(RESULTS_DIRECTORY)`
	python willireply/models/base_model.py

visualize:
	for result in `ls -1 $(RESULTS_DIRECTORY)/*.html`; do\
	  open $$result ; \
	done