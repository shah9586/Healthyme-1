import csv


csv.field_size_limit(100000000)

inp = r"C:\data\off.csv.csv"
out = r"core\data\india_products.tsv"

fields = [
    "code",
    "product_name",
    "ingredients_text",
    "categories",
    "brands",
    "countries",
    "countries_tags",
]

count = 0

with open(inp, "r", encoding="utf-8", errors="ignore") as f_in, \
     open(out, "w", encoding="utf-8", newline="") as f_out:

    reader = csv.DictReader(f_in, delimiter="\t")
    writer = csv.DictWriter(f_out, fieldnames=fields, delimiter="\t")
    writer.writeheader()

    for row in reader:
        countries = (row.get("countries") or row.get("countries_en") or "").lower()
        tags = (row.get("countries_tags") or "").lower()

        if "india" in countries or "en:india" in tags:
            writer.writerow({k: row.get(k, "") for k in fields})
            count += 1

            if count % 1000 == 0:
                print("Saved", count)

print("Done:", count)