import requests
from bs4 import BeautifulSoup
import copy
import csv

dataset = {
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
        if (index)  % 10 == 0 and index != 0:
            print("Processed", index, "Datasets...")
        current_dataset = copy.deepcopy(dataset)
        line = line.strip()

        response = requests.get(line)
        soup = BeautifulSoup(response.text, "html.parser")

        # Filling in the fields of the dataset
        name_tag = soup.find("h1") or soup.find("h2")
        if name_tag:
            current_dataset["Name"] = name_tag.get_text(strip=True)

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

                    if key == "SourceDatajsonIdentifier":
                        try:
                            current_dataset[key] = int(td_text)
                        except ValueError:
                            current_dataset[key] = td_text
                    else:
                        current_dataset[key] = td_text
        
        mailto_tag = soup.find("a", title="contact")
        
        current_dataset["PublisherEmailAddress"] = mailto_tag["href"].replace("mailto:", "").strip()
        
        section = soup.find("section", id="dataset-metadata-source")
        current_dataset["MetadataSource"] = "https://catalog.data.gov" + section.find("p", class_="description").find("a")["href"]
        current_dataset["HarvestSourceLink"] = "https://catalog.data.gov" + section.find("p", class_="text-muted").find("a")["href"]
        
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
        current_publisher["Name"] = mailto_tag.get_text(strip=True)
        current_publisher["Description"] = ""
        current_publisher["OrganizationType"] = soup.find('span', class_='organization-type').get_text(strip=True)
        if soup.find('p', class_='read-more'):
            current_publisher["read-more"] = "https://catalog.data.gov" + soup.find('p', class_='read-more').find('a')['href']
        else:
            if soup.find(id="organization-info").find("p", class_="description"):
                current_publisher["Description"] = soup.find(id="organization-info").find('p', class_='description').get_text(strip=True)
        all_publishers.append(current_publisher)

        # Filling in Dataset Tags
        for a in soup.select("section.tags a.tag"):
            all_dataset_tags.append({"DatasetIdentifier": current_dataset["Identifier"], "Tag": a["title"]})

        # Filling in the files
        for item in soup.select('li.resource-item'):
            fmt_text = item.select_one('.format-label').text.strip()
            
            download_btn = item.select_one('a.btn[data-format]')
            link = download_btn["href"]
            
            if link and fmt_text:
                all_files.append({'Link': link, 'Format': fmt_text, "DatasetIdentifier": current_dataset['Identifier']})
        
        # Filling in the dataset topics
        topic_list = soup.find("ul", class_="topics")
        if topic_list:
            for item in topic_list.find_all("li", class_="nav-item"):
                dataset_topics.append({
                        "DatasetIdentifier": current_dataset["DatasetIdentifier"],
                        "Topic": item.get_text(strip=True)
                    })


print("PROCESSING DATASETS COMPLETED")
print("PROCESSING USERS")

INPUT_FILE = "users.csv"
OUTPUT_FILE = "users_processed.csv"

with open(INPUT_FILE, newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    rows = list(reader)

output_fieldnames = ["EmailAddress", "Username", "Password", "Country", "Gender", "Birthdate"]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
    writer.writeheader()

    for index, row in enumerate(rows, start=1):
        if index % 10 == 0 and index:
            print("Processed", index, "Users...")
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
    if index % 10 == 0 and index:
        print("Processed", index, "Publishers...")
    if publisher["read-more"]:
        response = request.get(publisher["read-more"])
        soup = BeautifulSoup(response.text, "html.parser")
        publisher["Description"] = soup.find("div", class_="primary").find("p").get_text(strip=True)
        del publisher["read-more"]

print("PROCESSING COMPLETED")
