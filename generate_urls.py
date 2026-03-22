file_path = "urls.txt"
url_base = "https://catalog.data.gov/dataset/?page="

print("Starting generate_urls.py...")

with open(file_path, "w") as file:
    for i in range(1, 101):
        if i % 10 == 0:
            print("Generated", i, "URLS")
        file.write((url_base + str(i)) + "\n")

print("GENERATED ALL URLS")
