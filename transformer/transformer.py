from datetime import datetime

import pandas as pd


class Agent:

    FIELDS = {
        "ishare": {
            "prefix": "exchange_",
            "columns": [
                "Ticker",
                "Issuer Ticker#Ticker",
                "Name#$ishares_name",
                "Sector#$ishares_sector",
                "$ISIN",
                "Exchange#$ishares_exchange_name",
                "Location#$country_name",
                "Index#$ishares_index",
                "Date#$ishares_date",
                "Calculated Weight#$weight",
            ],
        }
    }

    def __init__(self, data):
        self.data = data
        self.dataframe = None

    def transform(self):
        result = []

        for row in self.data:

            _row = {}

            for field in self.FIELDS:
                data = self.FIELDS[field]

                prefix = data["prefix"]
                columns = data["columns"]

                for column in columns:
                    key = column
                    if "#" in column:
                        key, new_key = column.split("#")
                    else:
                        new_key = column

                    if "$" in new_key:
                        new_key = new_key.replace("$", "")
                        if "$" in key:
                            key = key.replace("$", "")

                    else:
                        new_key = prefix + new_key

                    if "*" in column:
                        new_key = new_key.replace("*", "")
                        if "*" in key:
                            key = key.replace("*", "")

                        if key not in row:
                            _row[new_key] = None
                            continue

                    new_key = new_key.lower()

                    if key in row:
                        if key not in [
                            "Ticker",
                            "OPENFIGI Ticker",
                            "securityDescription",
                        ]:
                            _row[new_key] = self.format_numbers(row[key])
                        else:
                            _row[new_key] = row[key]

            _row["timestamp_created_utc"] = self.timenow()
            result.append(_row)

        self.dataframe = pd.DataFrame(result)
        self.dataframe.sort_values(by=["ishares_index"], inplace=True)
        self.dataframe.reset_index(drop=True, inplace=True)
        return self.dataframe

    @staticmethod
    def format_numbers(value):
        if value in ["NaN", "", 0, None, "-"]:
            return None
        elif isinstance(value, str):
            if value == "INF":
                return value

            try:
                return round(float(value), 4)
            except Exception:
                return value
        elif isinstance(value, int):
            return round(float(value), 4)
        else:
            return value

    @staticmethod
    def timenow():
        return datetime.utcnow()
