import io
import json
import math
import random
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

from config import logger, settings


class iShare:

    PROXY = settings.BRIGHTDATA_PROXY
    PORT = settings.BRIGHTDATA_PORT
    USER = settings.BRIGHTDATA_USER
    PASSWD = settings.BRIGHTDATA_PASSWD

    TIME_OUT = 10
    WAIT_TIME = 5
    MAX_RETRY = 4

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

    FILTERED_FIELD = [
        "FX Rate",
        "Nominal",
        "Price",
        "Accrual Date",
        "Notional Value",
        "Shares",
    ]

    def __init__(self):
        self.dataframes = []

    def request(self, url, retry=0):
        try:
            r = requests.get(url, headers=self.HEADERS, proxies=self.get_proxy())
            if r.status_code == 200:
                return True, r
            elif r.status_code == 403:
                logger.error("403 HTTP response recieved. Retrying with a new proxy.")
                raise Exception
            else:
                return False, r
        except Exception:
            if retry > self.MAX_RETRY:
                return False

            retry += 1
            time.sleep(self.TIME_OUT)
            return self.request(url, retry=retry)

    def __fetch__(self, url, index, skip_rows):
        try:
            dataframe = self.fetch_json(url)
        except Exception as e:
            logger.error(f"Failed to fetch JSON data from {index} {url}")
            return False, None

        try:
            date = self.extract_date(url, skip_rows)
        except Exception as e:
            logger.warning(f"Failed to extract date from csv {index} {url}")
            return False, None

        self.add_marketvalue(dataframe)
        self.add_index(dataframe, index)
        self.add_date(dataframe, date)

        if skip_rows == 2:
            dataframe.rename(columns={"Issuer Ticker": "Ticker"}, inplace=True)

        elif skip_rows == 9:
            if "Russell" in index:
                dataframe["Location"] = "United States"

        self.dataframes.append(dataframe)
        return True, dataframe

    def concat(self):
        self.dataframe = pd.concat(self.dataframes, ignore_index=True)
        self.filter_df_columns()
        return self.dataframe

    def fetch_json(self, url):
        rows = []
        columns = self.extract_columns(url)
        columns = {len(columns): columns}
        url = url.split("?")[0] + "?tab=all&fileType=json"
        _, req = self.request(url)
        data = json.load(io.StringIO(req.content.decode("utf-8-sig")))["aaData"]
        for row in data:
            elements = []
            for item in row:
                if isinstance(item, dict):
                    elements.append(item["raw"])
                else:
                    elements.append(item)

            newrow = dict(zip(columns[len(elements)], elements))
            rows.append(newrow)

        return pd.DataFrame(rows)

    def extract_date(self, url, skip_rows):
        _, req = self.request(url)
        return self.__extract_date(io.StringIO(req.content.decode("utf-8")), skip_rows)

    def __extract_date(self, csv, skip_rows):
        if skip_rows == 2:
            df = pd.read_csv(csv, nrows=1)
            date = list(df.keys())[1]
            date = parse(date).date().__str__()
            return datetime.strptime(date, "%Y-%m-%d")

        elif skip_rows == 9:
            df = pd.read_csv(csv, nrows=1)
            date = df.to_numpy().tolist()[0][0]
            date = parse(date).date().__str__()
            return datetime.strptime(date, "%Y-%m-%d")

        return False

    def extract_columns(self, url):
        url = url.split(".ajax")[0]
        _, response = self.request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        div = soup.find("div", {"id": "tabsAll"})
        ths = div.find_all("th")
        return [
            ("Ticker" if "Issuer Ticker" == th.text.strip() else th.text.strip())
            for th in ths
        ]

    def filter_df_columns(self):
        if not len(self.FILTERED_FIELD):
            return

        for column in self.FILTERED_FIELD:
            if column in self.dataframe.columns.to_list():
                del self.dataframe[column]

    def get_proxy(self):
        session = random.random()
        proxies = {
            "http": f"http://{self.USER}-session-{session}:{self.PASSWD}@{self.PROXY}:{self.PORT}"
        }
        proxies["https"] = proxies["http"]
        return proxies

    @staticmethod
    def add_index(dataframe, index):
        dataframe["Index"] = index

    @staticmethod
    def add_date(dataframe, date):
        dataframe["Date"] = date

    @staticmethod
    def add_currency(dataframe, currency):
        dataframe["Currency"] = currency

    @staticmethod
    def add_marketvalue(dataframe):
        _sum = 0
        for _, row in dataframe.iterrows():
            column = "Market Value"
            if not (isinstance(row[column], float) and math.isnan(row[column])):
                value = str(row[column]).replace(",", "")
                _sum += float(value)

        dataframe["MarketValueSum"] = _sum
