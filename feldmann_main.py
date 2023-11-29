import os
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt

from commons import *


def run():
    # Load data
    chart_manager = ChartManager()
    chart_manager.load("Data/MSCI GLOBAL.csv")

    window_size = 14

    # Compute RSI
    diff = chart_manager.chart["Close"].diff()
    gain = (diff.clip(lower=0)).fillna(0)
    loss = (-diff.clip(upper=0)).fillna(0)
    avg_gain = gain.rolling(window=window_size, min_periods=1).mean()
    avg_loss = loss.rolling(window=window_size, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    
    # So that the chart only starts when indicator is valid
    shift_n = rsi.first_valid_index()

    rsi = rsi.iloc[shift_n:].reset_index(drop=True)
    chart_manager.chart = chart_manager.chart.iloc[shift_n:].reset_index(drop=True)

    """
    Plot indicators with chart
    """
    axes: Axes  # Needed for intellisense
    fig, axes = plt.subplots(1, 1, num=1)

    axes.plot(
        chart_manager.chart["Date"], rsi, label=f"RSI ({window_size})", lw=0.5, color="red"
    )
    axes.plot(
        chart_manager.chart["Date"],
        chart_manager.chart["Close"],
        label="Closing Prices",
        lw=0.5,
        color="blue",
    )

    """
    Plot investing results
    """
    buying_signals = rsi > 60
    algorithm_course = chart_manager.calculate_return(buying_signals)

    plt.legend(loc="upper left")
    fig, axes = plt.subplots(1, 1, num=2)

    total_capital = 4000
    steps = 30
    monthly_capital = total_capital / len(chart_manager.chart) * steps

    invest_once_result = chart_manager.invest_once(chart_manager.chart["Close"], total_capital)
    axes.plot(
        chart_manager.chart["Date"],
        invest_once_result,
        label="All-in account",
        lw=0.5,
        color="blue",
    )

    invest_once_algorithm_result = chart_manager.invest_once(algorithm_course, total_capital)
    axes.plot(
        chart_manager.chart["Date"],
        invest_once_algorithm_result,
        label="All-in account via algorithm",
        lw=0.5,
        color="purple",
    )


    invest_monthly_result = chart_manager.invest_rolling(chart_manager.chart["Close"], 0, monthly_capital, steps)
    axes.plot(
        chart_manager.chart["Date"],
        invest_monthly_result,
        label="Monthly account",
        lw=0.5,
        color="red",
    )

    invest_monthly_algorithm_result = chart_manager.invest_rolling(algorithm_course, 0, monthly_capital, steps)
    axes.plot(
        chart_manager.chart["Date"],
        invest_monthly_algorithm_result,
        label="Monthly account via algorithm",
        lw=0.5,
        color="brown",
    )

    no_invest_monthly_result = chart_manager.invest_rolling(np.repeat(1, len(chart_manager.chart)), 0, monthly_capital, steps)
    axes.plot(
        chart_manager.chart["Date"],
        no_invest_monthly_result,
        label="Saving money monthly",
        lw=0.5,
        alpha=0.5,
        color="green",
    )

    plot_profit_fields(axes, buying_signals, invest_once_algorithm_result, chart_manager.chart["Date"])

    print(f"""
Final amount for All-in account: {round(invest_once_result[-1], 1)} $
Final amount for All-in account via algorithm: {round(invest_once_algorithm_result[-1], 1)} $
Final amount for Monthly account: {round(invest_monthly_result[-1], 1)} $
Final amount for Monthly account via algorithm: {round(invest_monthly_algorithm_result[-1], 1)} $
Final amount for just saving: {round(no_invest_monthly_result[-1], 1)} $
""")

    plt.legend(loc="upper left")
    plt.show()


if __name__ == "__main__":
    run()
