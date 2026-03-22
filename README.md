# Dataset Scraper Pipeline

This project implements a complete multi-stage scraping pipeline to extract the first **2000 datasets** from the Data.gov catalog.

The scraping process is divided into four stages:

1. Generate listing page URLs
2. Scrape dataset detail page URLs
3. Scrape dataset data and associated files
4. Run the full pipeline from a single entry point

We iterate through:

[https://catalog.data.gov/dataset/?page=1](https://catalog.data.gov/dataset/?page=1)

up to:

[https://catalog.data.gov/dataset/?page=100](https://catalog.data.gov/dataset/?page=100)

---

# Project Structure

```id="w9z2ld"
dataset-scraper/
│
├── generate_urls.py
├── dataset_url_scraper.py
├── scraper.py
├── run_pipeline.py
├── urls.txt
├── users.csv
├── dataset_urls.txt
├── output/
│   ├── users_processed.csv
│   ├── publishers.csv
│   └── datasets.csv
│   ├── dataset_tags.csv
│   ├── projects.csv
│   ├── project_datasets.csv
│   ├── files.csv
│   ├── maintainers.csv
│   └── dataset_topics.csv
│
└── README.md
```

---

# Stage 1 — Generate Listing Page URLs

## generate_urls.py

Generates listing page URLs from page 1 to page 100:

[https://catalog.data.gov/dataset/?page=1](https://catalog.data.gov/dataset/?page=1)
...
[https://catalog.data.gov/dataset/?page=100](https://catalog.data.gov/dataset/?page=100)

### Responsibilities

* Generate all listing page URLs
* Store them in `urls.txt`
* One URL per line

---

# Stage 2 — Scrape Dataset Detail URLs

## dataset_url_scraper.py

This script collects dataset detail page URLs.

### Responsibilities

1. Read page URLs from `urls.txt`
2. Visit each page
3. Extract dataset detail page links
4. Collect dataset URLs
5. Store them in `dataset_urls.txt`

Each line in `dataset_urls.txt` represents one dataset detail page.

---

# Stage 3 — Scrape Dataset Data

## scraper.py

This is the main data extraction script.

### Responsibilities

1. Read dataset URLs from `dataset_urls.txt`
2. Visit each dataset page
3. Extract dataset data according to the ERD
4. Extract associated downloadable files/resources
5. Scrape and extract publishers' descriptions
6. Write and create CSV files for extracted data

---

# Stage 4 — Run the Entire Pipeline

## run_pipeline.py

This script serves as the single entry point for the entire project.

### Responsibilities

1. Execute `generate_urls.py`
2. Execute `dataset_url_scraper.py`
3. Execute `scraper.py`

This allows the entire scraping process to be executed with a single command.

---

# Output Files

All output is written to the `output/` directory.

Only the following files must be generated:

## 1. publishers.csv

* Contains publishing organizations
* One row per publisher
* Duplicate entries may exist, but this will be handled as we load the CSV into the database
* Structure of the file is like that of the prospective table in the database

---

## 2. datasets.csv

* Contains the scraped information about 2000 datasets
* One row per dataset
* Each dataset references its corresponding publisher
* Structure of the file is like that of the prospective table in the database

---

## 3. files.csv

* Contains links to the resources associated with datasets
* One row per file/resource
* Structure of the file is like that of the prospective table in the database

---

## 4. users_processed.csv

* A reorganized version of the `users.csv` file to match table order
* Created a standard password for all users `admin123` (This is for testing purposes. In production, I know that I need to encrypt passwords)
* Structure of the file is like that of the prospective table in the database

---

## 5. dataset_tags.csv

* Stores the tag associated with each dataset, using the dataset identifier as a foreign key
* Structure of the file is like that of the prospective table in the database

---

## 6. projects.csv

* An empty file for the projects of each user. I created this file (even though it is empty) for my own reference.
* Structure of the file is like that of the prospective table in the database

---

## 7. project_datasets.csv

* An empty file linking the projects of each user with datasets they use. I created this file (even though it is empty) for my own reference.
* Structure of the file is like that of the prospective table in the database

---

## 8. maintainers.csv

* Stores the maintainers for the available datasets
* Structure of the file is like that of the prospective table in the database

---

## 9. dataset_topics.csv

* Stores the topics of the datasets
* Structure of the file is like that of the prospective table in the database



Run the pipeline using:

1. `run_pipeline.py`

This will automatically:

* Generate listing page URLs
* Collect 2000 dataset detail URLs
* Scrape dataset data
* Produce necessary CSV files

The process completes once 2000 datasets and their associated files have been successfully stored in the `output/` directory.
