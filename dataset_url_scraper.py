import requests
from bs4 import BeautifulSoup

pages_url_file = "urls.txt"

datasets_url_file = "datasets_urls.txt"

dataset_num = 0

page_num = 0

print('Starting dataset_url_scraper.py...')

with open(pages_url_file, "r") as f_in, open(datasets_url_file, "w") as f_out:
    for index, line in enumerate(f_in, start=1):
        page_num += 1
        line = line.strip()
        
        response = requests.get(line)
        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.select("h3.dataset-heading a")

        for link in links:
            dataset_num += 1
            url = link.get('href')
            f_out.write("https://catalog.data.gov" + url + "\n")
        
        if index % 10:
            print("Scraped", index, "pages for dataset URLs")

print("Gathered", dataset_num, "dataset URLs from", page_num, "pages")
