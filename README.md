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
* Overwrite the file if it already exists

---

# Stage 2 — Scrape Dataset Detail URLs

## dataset_url_scraper.py

This script collects dataset detail page URLs.

### Responsibilities

1. Read listing URLs from `urls.txt`
2. Visit each listing page
3. Extract dataset detail page links
4. Collect **2000 unique dataset URLs**
5. Store them in `dataset_urls.txt`
6. Ensure no duplicates
7. Stop immediately after reaching 2000 unique URLs

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
5. Deduplicate publishers
6. Write structured CSV files
7. Stop after processing 2000 datasets

---

# Stage 4 — Run the Entire Pipeline

## run_pipeline.py

This script serves as the **single entry point** for the entire project.

### Responsibilities

1. Execute `generate_urls.py`
2. Execute `dataset_url_scraper.py`
3. Execute `scraper.py`
4. Ensure the steps run in the correct order
5. Stop execution if any stage fails
6. Provide clear console output indicating progress

This allows the entire scraping process to be executed with a single command.

---

# Output Files

All output is written to the `output/` directory.

Only the following files must be generated:

## 1. publisher.csv

* Contains unique publishing organizations
* One row per publisher
* No duplicate entries

---

## 2. dataset.csv

* Contains up to 2000 datasets
* One row per dataset
* Each dataset references its corresponding publisher

---

## 3. files.csv

* Contains downloadable resources associated with datasets
* One row per file/resource
* Supports many-to-one relationship with datasets

---

# Full Execution Flow

Run the pipeline using:

1. `run_pipeline.py`

This will automatically:

* Generate listing page URLs
* Collect 2000 dataset detail URLs
* Scrape dataset data
* Produce:

  * `publisher.csv`
  * `dataset.csv`
  * `files.csv`

The process completes once 2000 datasets and their associated files have been successfully stored in the `output/` directory.

