import json
import os
import time
import datetime
from nseindia import NseIndia

# data = nse_data.get_oi_spurt()
# if data is not None:
#     data = data["data"]
# print(json.dumps(data, indent=2))
# if data:
#     headers = data[0].keys()  # Get headers dynamically from the first entry
#     table = tabulate(data, headers="keys", tablefmt="fancy_grid")
#     print(table)

# premarket_data = nse_data.get_pre_martket()
# if premarket_data is not None:
#     print(json.dumps(premarket_data, indent=2))

# market_status = nse_data.is_market_open()
# print(market_status)


def write_to_file(data, filename="output.json"):
    """Writes the data list to a JSON file."""
    if os.path.exists(filename):
        # Read existing file
        with open(filename, "r") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # Append new data to the list
    existing_data.append(data)

    # Write updated list back to the file
    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=4)


def main():
    nse_india = NseIndia()
    start_time = datetime.time(9, 30)  # Start time: 9:30 AM
    end_time = datetime.time(15, 40)  # End time: 3:40 PM
    filename = "output.json"
    checked_date = None  # Store the last date the market status was checked
    prev_pre_market_fo_stocks_data = {}
    prev_fo_stocks_data = {}

    while True:  # Infinite loop for daily execution
        json_data = {}
        now = datetime.datetime.now()
        current_date = now.date()

        # Check market status only once per day
        if current_date != checked_date:
            is_open_today = nse_india.is_market_open()
            checked_date = current_date  # Update checked date
            if not is_open_today:
                print(
                    f"Market is closed on {current_date}. Waiting for the next day..."
                )
                while current_date == datetime.datetime.now().date():
                    time.sleep(60)  # Wait 1 minute before checking the date again
                continue  # Recheck the market status the next day

        # Proceed with capturing data if the market is open and within trading hours
        current_time = now.time()
        if start_time <= current_time <= end_time:
            # get data using desired method
            pre_market_fo_stocks_data = nse_india.get_pre_martket()
            fo_stocks_data = nse_india.get_fo_stocks_data()

            # make the data none if it was equal to previously fetched data
            if pre_market_fo_stocks_data == prev_pre_market_fo_stocks_data:
                pre_market_fo_stocks_data = None
            else:
                prev_pre_market_fo_stocks_data = pre_market_fo_stocks_data
            if fo_stocks_data == prev_fo_stocks_data:
                prev_fo_stocks_data = None
            else:
                prev_fo_stocks_data = fo_stocks_data

            json_data["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp
            cap_data = {
                "pre_market_fo_stocks": pre_market_fo_stocks_data,
                "fo_stocks": fo_stocks_data,
            }
            json_data["data"] = cap_data

            # Check if the data is the same as the last captured data
            write_to_file(json_data, filename)
            time.sleep(60)  # Wait 1 minute before capturing again

        elif current_time > end_time:
            # Wait until the next day's start time
            print("End time reached. Waiting for the next day...")
            while current_date == datetime.datetime.now().date():
                time.sleep(60)  # Wait 1 minute before checking the date again


if __name__ == "__main__":
    main()
