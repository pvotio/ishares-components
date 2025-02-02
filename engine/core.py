import math
import threading

from engine import ishare, utils


class Engine:

    ISHARES_HOLDINGS = utils.ISHARES_HOLDINGS

    def __init__(self):
        self.status = None
        self.threads = []
        self.result = []

    def run(self):
        i = ishare.iShare()

        for csv in self.ISHARES_HOLDINGS:
            t = threading.Thread(target=i.__fetch__, args=(csv[0], csv[1], csv[2]))

            self.threads.append(t)

        [t.start() for t in self.threads]
        [t.join() for t in self.threads]

        self.threads = []

        dataframe = i.concat()
        dataframe["source"] = "docker"

        result = self.convert_df_to_list(dataframe)

        for row in result:
            row = self.calculate_weight(row)
            self.result.append(row)

        self.status = True
        return self.result

    def convert_df_to_list(self, dataframe):
        result = [
            row.to_dict()
            for _, row in dataframe.iterrows()
            if not self.is_nan(row["Ticker"])
        ]
        return result

    def calculate_weight(self, row):
        market_value = self.format_numbers(row["Market Value"])
        overall_value = self.format_numbers(row["MarketValueSum"])
        row["Calculated Weight"] = (market_value / overall_value) * 100
        return row

    @staticmethod
    def format_numbers(value):
        if isinstance(value, float) or isinstance(value, int):
            return value

        value_copy = value
        for ch in ".,-+%":
            value_copy = value_copy.replace(ch, "")

        if value_copy.isdigit():
            if "." in value:
                for ch in ",+%":
                    if ch in value:
                        value = value.replace(ch, "")

                return float(value)
            else:
                return int(value_copy)
        else:
            return value

    @staticmethod
    def is_nan(num):
        return (isinstance(num, float) and math.isnan(num)) or str(num) == "-"
