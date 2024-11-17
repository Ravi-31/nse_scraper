import json
from nsepython import nse_get_top_gainers
from tabulate import tabulate


data = nse_get_top_gainers().to_dict(orient="records")
print(json.dumps(data, indent=2))


# Extract the fields to display in the table
keys_to_display = [
    "symbol",
    "open",
    "dayHigh",
    "dayLow",
    "lastPrice",
    "previousClose",
    "change",
    "pChange",
    "totalTradedVolume",
    "yearHigh",
    "yearLow",
]
filtered_data = [{key: item[key] for key in keys_to_display} for item in data]
# Display the table
# print(tabulate(filtered_data, headers="keys", tablefmt="grid"))