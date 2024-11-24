import json
import os
import time
import datetime
from nseindia import NseIndia
from highlight_diff import highlight_diff


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
    start_time = datetime.time(9, 15)  # Start time: 9:30 AM
    end_time = datetime.time(15, 32)  # End time: 3:40 PM
    filename = "output.json"
    checked_date = None  # Store the last date the market status was checked
    prev_pre_market_fo_stocks_data = {}
    prev_fo_stocks_data = {}
    prev_fo_spurt = {}

    while True:  # Infinite loop for daily execution
        json_data = {}
        now = datetime.datetime.now()
        current_date = now.date()
        # print(current_date, now.time(), type(start_time))

        # Check market status only once per day
        if current_date != checked_date:
            is_open_today = nse_india.is_market_open()
            checked_date = current_date  # Update checked date
            if not is_open_today:
                print(
                    f"Market is closed on {current_date}. Waiting for the next day..."
                )
                while current_date == datetime.datetime.now().date():
                    print("sleeping 1m")
                    time.sleep(40)  # Wait 1 minute before checking the date again

                continue  # Recheck the market status the next day
            else:
                print(
                    f"Market is open on {current_date}. Scraping will start on designated time."
                )


        # Proceed with capturing data if the market is open and within trading hours
        current_time = now.time()
        if start_time <= current_time <= end_time:
            # get data using desired method
            pre_market_fo_stocks_data = nse_india.get_pre_martket()
            fo_stocks_data = nse_india.get_fo_stocks_data()
            fo_spurt = nse_india.get_oi_spurt()
            for i in pre_market_fo_stocks_data["data"]:
                del i["metadata"]["purpose"]

            # make the data none if it was equal to previously fetched data
            if pre_market_fo_stocks_data == prev_pre_market_fo_stocks_data:
                pre_market_fo_stocks_data = None
            else:
                # highlight_diff(
                #     prev_pre_market_fo_stocks_data, pre_market_fo_stocks_data
                # )
                prev_pre_market_fo_stocks_data = pre_market_fo_stocks_data
            if fo_stocks_data == prev_fo_stocks_data:
                fo_stocks_data = None
            else:
                # highlight_diff(prev_fo_stocks_data, fo_stocks_data)
                prev_fo_stocks_data = fo_stocks_data
            if prev_fo_spurt == fo_spurt:
                fo_spurt = None
            else:
                prev_fo_spurt = fo_spurt
                

            json_data["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")  # Add timestamp
            cap_data = {
                "pre_market_fo_stocks": pre_market_fo_stocks_data,
                "fo_stocks": fo_stocks_data,
                "fo_spurt": fo_spurt
            }
            json_data["data"] = cap_data
            print_data(json_data, prev_fo_stocks_data, prev_fo_spurt)

            # Check if the data is the same as the last captured data
            write_to_file(json_data, filename)
            print("sleeping 1m")
            time.sleep(40)  # Wait 1 minute before capturing again

        elif current_time > end_time:
            # Wait until the next day's start time
            print("End time reached. Waiting for the next day...")
            while current_date == datetime.datetime.now().date():
                print("sleeping 1m")
                time.sleep(40)  # Wait 1 minute before checking the date again

def print_data(json_data, prev_fo_stocks_data, prev_fo_spurt):
    print(f"\n{json_data['timestamp']}\n")

    # Retrieve current data or fallback to previous data if current data is None
    pre_markt = json_data["data"]["pre_market_fo_stocks"]
    fo_stock = json_data["data"]["fo_stocks"] if json_data["data"]["fo_stocks"] is not None else prev_fo_stocks_data
    fo = json_data["data"]["fo_spurt"] if json_data["data"]["fo_spurt"] is not None else prev_fo_spurt

    # Define functions to print symbols in green or red
    def print_symbol_in_green(string):
        return f"\033[92m{string}\033[0m"

    def print_symbol_in_red(string):
        return f"\033[91m{string}\033[0m"

    # Handle pre-market FO stocks
    if pre_markt is not None:
        data = pre_markt["data"]
        threshold = 2
        filtered_sorted_data = sorted(
            [d for d in data if abs(d['metadata']['pChange']) >= threshold],
            key=lambda x: x['metadata']['pChange'],
            reverse=True
        )
        print("\nPremarket\n")
        for i, item in enumerate(filtered_sorted_data):
            print(f"{i+1}. {item['metadata']['symbol']} - pChange: {item['metadata']['pChange']:.2f}")

    print("\n" * 2)

    # Filter and sort FO stocks data based on the threshold
    filtered_sorted_fo_stock = []
    negative_common_symbols = set()  # Track common symbols with negative pChange
    if fo_stock is not None:
        data = fo_stock["data"]
        threshold = 2
        filtered_sorted_fo_stock = sorted(
            [d for d in data if abs(d['pChange']) >= threshold],
            key=lambda x: x['pChange'],
            reverse=True
        )
        # Collect symbols that are both common and have a negative pChange
        negative_common_symbols = {
            d['symbol'] for d in filtered_sorted_fo_stock if d['pChange'] < 0
        }

    # Filter and sort FO spurt data based on the threshold
    filtered_sorted_fo_spurt = []
    if fo is not None:
        data = fo["data"]
        threshold = 2
        filtered_sorted_fo_spurt = sorted(
            [d for d in data if d["avgInOI"] >= threshold],
            key=lambda x: x["avgInOI"],
            reverse=True
        )

    # Check for common symbols in the filtered lists
    common_symbols = {
        item['symbol'] for item in filtered_sorted_fo_stock
    }.intersection({
        item['symbol'] for item in filtered_sorted_fo_spurt
    })

    # Only keep symbols that are both common and have a negative pChange
    negative_common_symbols.intersection_update(common_symbols)

    # Print FO Stocks Movers, making common symbols green and negative pChange symbols red
    if fo_stock is not None:
        print("\nFO Stocks Movers\n")
        for i, item in enumerate(filtered_sorted_fo_stock):
            symbol = item['symbol']
            pChange = item['pChange']

            if symbol in common_symbols and symbol in negative_common_symbols:
                print(f"{i+1}. {print_symbol_in_red(symbol)} => {pChange:.2f}%")
            elif symbol in common_symbols:
                print(f"{i+1}. {print_symbol_in_green(symbol)} => {pChange:.2f}%")
            else:
                print(f"{i+1}. {symbol} => {pChange:.2f}%")

    # Print FO OI Spurt Movers, making only common negative symbols red
    if fo is not None:
        print("\nFO OI Spurt Movers\n")
        for i, item in enumerate(filtered_sorted_fo_spurt):
            symbol = item['symbol']
            avgInOI = item['avgInOI']

            if symbol in common_symbols and symbol in negative_common_symbols:
                print(f"{i+1}. {print_symbol_in_red(symbol)} => avgInOI: {avgInOI:.2f}%")
            elif symbol in common_symbols:
                print(f"{i+1}. {print_symbol_in_green(symbol)} => avgInOI: {avgInOI:.2f}%")
            else:
                print(f"{i+1}. {symbol} => avgInOI: {avgInOI:.2f}%")

    print()
        


if __name__ == "__main__":
    main()
