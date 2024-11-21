import requests
import datetime
import json


class NseIndia:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.fo_api = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
        self.oi_spurt_api = (
            "https://www.nseindia.com/api/live-analysis-oi-spurts-underlyings"
        )
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9,en-IN;q=0.8,en-GB;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
        }

    def _cookie_format(self, cookie_string):
        result = {}
        for section in cookie_string.split(", "):
            for part in section.split("; "):
                if "=" in part:
                    key, value = part.split("=", 1)
                    result[key.strip()] = value.strip()
                else:
                    result[part.strip()] = True
        return result

    def nsefetch(self, website, method="new"):
        # library implementation
        if method == "new":
            try:
                output = requests.get(website, headers=self.headers).json()
            except ValueError:
                s = requests.Session()
                output = s.get(self.base_url, headers=self.headers)
                output = s.get(website, headers=self.headers).json()
            return output

        # my implementation
        if method == "old":
            response = requests.get(self.base_url, headers=self.headers)
            set_cookie = response.headers.get("Set-Cookie")
            cookie_format = self._cookie_format(set_cookie)
            headers = {
                # "accept": "*/*",
                # "accept-language": "en-US,en;q=0.9",
                # "cache-control": "no-cache",
                # "pragma": "no-cache",
                # "priority": "u=1, i",
                # "referer": "https://www.nseindia.com/market-data/oi-spurts",
                # "sec-ch-ua": '"Chromium";v="129", "Not=A?Brand";v="8"',
                # "sec-ch-ua-mobile": "?0",
                # "sec-ch-ua-platform": '"Linux"',
                # "sec-fetch-dest": "empty",
                # "sec-fetch-mode": "cors",
                # "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            }

            # Dynamically build the cookie string
            cookie_string = "; ".join(
                f"{key}={value}" for key, value in cookie_format.items()
            )
            headers["cookie"] = cookie_string

            response = requests.get(url=website, headers=headers)

            # Handle response
            if response.status_code == 200:
                return response.json()  # Assuming the API returns JSON
            else:
                print(f"Request failed with status code {response.status_code}")
                print(response.text)
                return {}  # Assuming the API returns JSON

    def get_fo_stocks_data(self):
        data = self.nsefetch(self.fo_api)
        return data
        # df = pd.DataFrame(positions['data'])
        # df = df.sort_values(by="pChange")

    def get_oi_spurt(self):
        data = self.nsefetch(self.oi_spurt_api, method="old")
        if data is not None:
            return {
                "data": data["data"],
                "timestamp": data["timestamp"],
                "currTradingDate": data["currTradingDate"],
                "prevTradingDate": data["prevTradingDate"],
            }

    def get_pre_martket(self, key="NIFTY"):
        """
        keys -> ALL, FO, NIFTY
        """
        data = self.nsefetch(
            f"https://www.nseindia.com/api/market-data-pre-open?key={key}"
        )
        return data

    def nse_holidays(self, type="trading"):
        if type == "clearing":
            payload = self.nsefetch(
                "https://www.nseindia.com/api/holiday-master?type=clearing"
            )
            return payload
        if type == "trading":
            payload = self.nsefetch(
                "https://www.nseindia.com/api/holiday-master?type=trading"
            )
            return payload
        return {}

    def is_market_open(self, segment="FO"):
        """
        Check if the market is open today for the given segment.
        Includes checks for holidays and weekends (Saturdays and Sundays).
        """
        # Fetch the holiday JSON for the segment
        holiday_json = self.nse_holidays()[segment]

        # Get today's date and day of the week
        today_date = datetime.date.today()
        today_date_str = today_date.strftime("%d-%b-%Y")
        today_weekday = today_date.weekday()  # 0 = Monday, 6 = Sunday

        # Check if today is a weekend
        if today_weekday in [5, 6]:  # 5 = Saturday, 6 = Sunday
            # print("Market is closed today because it's a weekend.")
            return False

        # Check if today is a holiday
        for holiday in holiday_json:
            if holiday["tradingDate"] == today_date_str:
                # print(f"Market is closed today because of {holiday['description']}")
                return False

        # If no holiday and not a weekend, the market is open
        # print("FNO Market is open today. Have a Nice Trade!")
        return True


# nse = NseIndia()
# data = nse.get_oi_spurt()
# import json
# print(json.dumps(data, indent=2))
