import requests
from bs4 import BeautifulSoup

pages_url_file = "urls.txt"


with open(pages_url_file, "r") as file:
    for line in file:
        line = line.strip()
        response = requests.get(line)

        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.select("h3.dataset-heading a")

        for link in links:
            print(link.get_text(strip=True))
