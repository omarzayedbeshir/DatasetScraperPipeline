file_path = "urls.txt"
url_base = "https://catalog.data.gov/dataset/?page="

with open(file_path, "w") as file:
    for i in range(1, 101):
        file.write((url_base + str(i)) + "\n")
