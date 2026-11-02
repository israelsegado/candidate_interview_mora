import csv

def write_csv(columns, rows, path):
    with open(path, 'w', encoding='utf8', newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)