import subprocess
import sys

scripts = ["generate_urls.py", "dataset_url_scraper.py", "scraper.py"]


print("Running run_pipeline.py...")
print("Starting scraping pipeline...")

for script in scripts:
    subprocess.run([sys.executable, script])
