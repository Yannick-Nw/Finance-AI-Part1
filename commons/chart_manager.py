from typing import Sequence
import numpy as np
import pandas as pd
import os
import numpy.typing as npt


class ChartManager:
    chart: pd.DataFrame = None

    def __init__(self):
        pass

    def load(self, name: str):
        path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "Data", f"{name}.csv"
        )
        df: pd.DataFrame = pd.read_csv(path, sep=",")
        df = df.dropna().reset_index(drop=True)
        df["Date"] = pd.to_datetime(df["Date"])

        self.chart = df

    def calculate_return(self, buying_signals: Sequence[bool]) -> Sequence[float]:
        if self.chart is None:
            raise Exception("Must first call 'load' before 'calculate_investment'!")

        df_iter = self.chart.iterrows()
        _, stock_entry = next(df_iter)

        algorithm_course = [stock_entry["Close"]]
        for i, stock_entry in df_iter:
            # Sell when there is a change. There is one day where you still buy while buying is false
            # this is because you could not have known that the change will come tomorrow so you have to hold it until
            # a change comes.
            # Because we are adding the last day we are always one day behind
            if (
                buying_signals[i]
                and buying_signals[i - 1]
                or not buying_signals[i]
                and buying_signals[i - 1]
            ):
                algorithm_course.append(
                    algorithm_course[-1]
                    + (stock_entry["Close"] - self.chart["Close"][i - 1])
                )
            else:
                algorithm_course.append(algorithm_course[-1])

        return np.array(algorithm_course) / algorithm_course[0]

    def invest_once(self, chart: Sequence[float], amount: int) -> Sequence[float]:
        return list((chart / chart[0]) * amount)

    def invest_rolling(
        self, chart: Sequence[float], amount: int, interval_days: int = 30
    ) -> Sequence[float]:
        total_days = len(chart)
        interval_amount = amount / total_days * interval_days
        
        bought_stocks = 0
        rolling_value = []
        for i in range(0, total_days):
            if i % interval_days == 0:
                bought_stocks += interval_amount / chart[i]
                
            rolling_value.append(bought_stocks * chart[i])

        return list(rolling_value)
