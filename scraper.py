import requests
from bs4 import BeautifulSoup
import copy
import csv
import time
import uuid

dataset = {
    "UUID": "",
    "Identifier": "",
    "Name": "",
    "Description": "",
    "Category": "",
    "BureauCode": "",
    "FirstPublished": "",
    "SourceHash": "",
    "LastModified": "",
    "MetadataCatalogID": "",
    "SourceSchemaVersion": "",
    "CatalogDescribedby": "",
    "HarvestObjectID": "",
    "HarvestSourceID": "",
    "AccessLevel": "",
    "MetadataSource": "",
    "License": "",
    "SchemaVersion": "",
    "HomepageURL": "",
    "MetadataCreationDate": "",
    "HarvestSourceTitle": "",
    "HarvestSourceLink": "",
    "MetadataUpdateDate": "",
    "SourceDatajsonIdentifier": 0,
    "ProgramCode": "",
    "MetadataContext": "",
    "MaintainerEmailAddress": "",
    "PublisherEmailAddress": ""
}

publisher = {
    "EmailAddress": "",
    "Name": "",
    "Description": "",
    "OrganizationType": ""
}

month_to_num = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

FIELD_MAP = {
    "Identifier": "Identifier",
    "Category": "Category",
    "Bureau Code": "BureauCode",
    "Data First Published": "FirstPublished",
    "Source Hash": "SourceHash",
    "Data Last Modified": "LastModified",
    "Metadata Catalog ID": "MetadataCatalogID",
    "Source Schema Version": "SourceSchemaVersion",
    "Catalog Describedby": "CatalogDescribedby",
    "Harvest Object Id": "HarvestObjectID",
    "Harvest Source Id": "HarvestSourceID",
    "Public Access Level": "AccessLevel",
    # "Metadata Source" : "MetadataSource",
    "License": "License",
    "Schema Version": "SchemaVersion",
    "Homepage URL": "HomepageURL",
    "Harvest Source Title": "HarvestSourceTitle",
    # "Harvest Source Link": "HarvestSourceLink",
    "Metadata Created Date" : "MetadataCreationDate",
    "Metadata Updated Date": "MetadataUpdateDate",
    "Source Datajson Identifier": "SourceDatajsonIdentifier",
    "Program Code": "ProgramCode",
    "Metadata Context": "MetadataContext",
    "Maintainer": "MaintainerEmailAddress",
    "Contact Email": "MaintainerEmailAddress",
    "Publisher Email Address": "PublisherEmailAddress",
}

print("Starting scraper.py...")
print("PROCESSING DATASETS...")

datasets_url_file = "datasets_urls.txt"

all_datasets = []
all_publishers = []
all_dataset_tags = []
all_files = []
all_maintainers = []
all_dataset_topics = []

with open(datasets_url_file, "r") as f_in:
    for index, line in enumerate(f_in, start=1):
        time.sleep(0.5)
        current_dataset = copy.deepcopy(dataset)
        line = line.strip()
        print("Processing Dataset: #" + str(index) + " at:", line)
        current_dataset["UUID"] = str(uuid.uuid4())
        response = requests.get(line)
        soup = BeautifulSoup(response.text, "html.parser")
        if not soup:
            continue
        # Filling in the fields of the dataset
        name_tag = soup.find("h1", itemprop="name") 
        if name_tag:
            current_dataset["Name"] = name_tag.get_text(strip=True)

        if soup.find("div", itemprop="description"):
            current_dataset["Description"] = soup.find("div", itemprop="description").get_text(strip=True)
        
        rows = soup.find_all("tr")
        for row in rows:
            th = row.find("th")
            td = row.find("td")
            if th and td:
                th_text = th.get_text(strip=True)
                td_text = td.get_text(strip=True)
                if th_text in FIELD_MAP:
                    key = FIELD_MAP[th_text]
            
                    if key == "MaintainerEmailAddress":
                        mailto_tag = td.find("a", href=lambda h: h and h.startswith("mailto:"))
                        if mailto_tag:
                            td_text = mailto_tag["href"].replace("mailto:", "").strip()
                            current_dataset[key] = td_text
                            all_maintainers.append({
                                    "EmailAddress": td_text,
                                    "Name": mailto_tag.get_text(strip=True)
                                })
                    elif key == "SourceDatajsonIdentifier":
                        try:
                            current_dataset[key] = int(td_text)
                        except ValueError:
                            current_dataset[key] = td_text
                    else:
                        current_dataset[key] = td_text
        
        mailto_tag = soup.find("a", title="contact")
        
        if mailto_tag:
            current_dataset["PublisherEmailAddress"] = mailto_tag["href"].replace("mailto:", "").strip()
        
        section = soup.find("section", id="dataset-metadata-source")
        
        if section:
            if section.find("p", class_="description"):
                MetadataSource = section.find("p", class_="description").find("a")
        
                if MetadataSource:
                    MetadataSource = MetadataSource["href"]
                    if MetadataSource.startswith("http://") or MetadataSource.startswith("https://"):
                        current_dataset["MetadataSource"] = MetadataSource
                    else:
                        current_dataset["MetadataSource"] = "https://catalog.data.gov" + MetadataSource

            HarvestSourceLink = section.find("p", class_="text-muted").find("a")
            
            if HarvestSourceLink:
                HarvestSourceLink = HarvestSourceLink["href"]
                if HarvestSourceLink.startswith("http://") or HarvestSourceLink.startswith("https://"):
                    current_dataset["HarvestSourceLink"] = HarvestSourceLink
                else:
                    current_dataset["HarvestSourceLink"] = "https://catalog.data.gov" + HarvestSourceLink

        if current_dataset["MetadataUpdateDate"]:
            segments = current_dataset["MetadataUpdateDate"].split()
            current_dataset["MetadataUpdateDate"] = segments[2] + "-" + str(month_to_num[segments[0]]) + "-" + segments[1][:-1]
        
        if current_dataset["MetadataCreationDate"]:
            segments = current_dataset["MetadataCreationDate"].split()
            current_dataset["MetadataCreationDate"] = segments[2] + "-" + str(month_to_num[segments[0]]) + "-" + segments[1][:-1]


        all_datasets.append(current_dataset)

        # Filling in the fields of the publisher
        current_publisher = copy.deepcopy(publisher)
        current_publisher["EmailAddress"] = current_dataset["PublisherEmailAddress"]
        if mailto_tag:
            current_publisher["Name"] = mailto_tag.get_text(strip=True)
        current_publisher["Description"] = ""
        if soup.find('span', class_='organzation-type'):
            current_publisher["OrganizationType"] = soup.find('span', class_='organization-type').get_text(strip=True)
        if soup.find('p', class_='read-more'):
            if soup.find('p', class_='read-more').find('a')['href']:
                current_publisher["read-more"] = "https://catalog.data.gov" + soup.find('p', class_='read-more').find('a')['href']
        elif soup.find(id="organization-info"):
            if soup.find(id="organization-info").find("p", class_="description"):
                current_publisher["Description"] = soup.find(id="organization-info").find('p', class_='description').get_text(strip=True)
        all_publishers.append(current_publisher)

        # Filling in Dataset Tags
        for a in soup.select("section.tags a.tag"):
            all_dataset_tags.append({"DatasetUUID": current_dataset["UUID"], "Tag": a["title"]})

        # Filling in the files
        for item in soup.select('li.resource-item'):
            fmt_text = item.select_one('.format-label').text.strip()
            
            download_btn = item.select_one('a.btn[data-format]')
            
            if download_btn:
                link = download_btn["href"]
            
            if link and fmt_text:
                all_files.append({'Link': link, 'Format': fmt_text, "DatasetUUID": current_dataset["UUID"]})
        
        # Filling in the dataset topics
        topic_list = soup.find("ul", class_="topics")
        if topic_list:
            for item in topic_list.find_all("li", class_="nav-item"):
                all_dataset_topics.append({
                        "DatasetUUID": current_dataset["UUID"],
                        "Topic": item.get_text(strip=True)
                    })

        with open("output/datasets.csv", "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_datasets[0].keys())
            writer.writeheader()
            writer.writerows(all_datasets)


with open("output/datasets.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_datasets[0].keys())
    writer.writeheader()
    writer.writerows(all_datasets)

print("PROCESSING DATASETS COMPLETED")
print("PROCESSING USERS")

OUTPUT_FILE = "output/users_processed.csv"

with open("users.csv", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

output_fieldnames = ["EmailAddress", "Username", "Password", "Country", "Gender", "Birthdate"]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
    writer.writeheader()

    for index, row in enumerate(rows, start=1):
        print("Processing User: #" + str(index))
        writer.writerow({
            "EmailAddress": row["email"],
            "Username":     row["username"],
            "Password":     "admin123",
            "Country":      row["country"],
            "Gender":       row["gender"],
            "Birthdate":    row["birthdate"],
        })

print("PROCESSING USERS COMPLETED")

print("PROCESSING PUBLISHERS")

for index, publisher in enumerate(all_publishers, start=1):
    print("Processing Publisher: #" + str(index) + " at", publisher.get("read-more"))
    if publisher.get("read-more"):
        time.sleep(0.5) 
        response = requests.get(publisher["read-more"])
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("div", class_="primary").find("p"):
            publisher["Description"] = soup.find("div", class_="primary").find("p").get_text(strip=True)
        del publisher["read-more"]

print("PROCESSING HTML COMPLETED")

print("CREATING CSV FILES")

with open("output/publishers.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_publishers[0].keys())
    writer.writeheader()
    writer.writerows(all_publishers)

with open("output/dataset_tags.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_dataset_tags[0].keys())
    writer.writeheader()
    writer.writerows(all_dataset_tags)

with open("output/projects.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["UserEmailAddress", "Name", "Category"])
    writer.writeheader()

with open("output/project_datasets.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["UserEmailAddress", "Name", "DatasetUUID"])
    writer.writeheader()
    
with open("output/files.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_files[0].keys())
    writer.writeheader()
    writer.writerows(all_files)

with open("output/maintainer.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_maintainers[0].keys())
    writer.writeheader()
    writer.writerows(all_maintainers)

with open("output/dataset_topics.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_dataset_topics[0].keys())
    writer.writeheader()
    writer.writerows(all_dataset_topics)

print("PROCESSING CSV FILES COMPLETED")
print("PROCESS COMPLETED")
