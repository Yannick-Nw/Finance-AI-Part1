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
from lib.visualization.plot_stock_strategy import plot_profit_fields


def run():
    # Load data
    chart_manager = ChartManager()
    chart_manager.load("MSCI GLOBAL")

    window_size = 100
    sma = chart_manager.chart["Close"].rolling(window=window_size).mean()

    # So that the chart only starts when indicator is valid
    shift_n = sma.first_valid_index()

    sma = sma.iloc[shift_n:].reset_index(drop=True)
    chart_manager.chart = chart_manager.chart.iloc[shift_n:].reset_index(drop=True)

    """
    Plot indicators with chart
    """
    axes: Axes  # Needed for intellisense
    fig, axes = plt.subplots(1, 1, num=1)

    axes.plot(
        chart_manager.chart["Date"], sma, label=f"{window_size} SMA", lw=0.5, color="red"
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
    buying_signals = chart_manager.chart["Close"] > sma
    algorithm_course = chart_manager.calculate_return(buying_signals)

    plt.legend(loc="upper left")
    fig, axes = plt.subplots(1, 1, num=2)

    total_capital = 4000

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


    invest_monthly_result = chart_manager.invest_rolling(chart_manager.chart["Close"], total_capital, 30)
    axes.plot(
        chart_manager.chart["Date"],
        invest_monthly_result,
        label="Monthly account",
        lw=0.5,
        color="red",
    )

    invest_monthly_algorithm_result = chart_manager.invest_rolling(algorithm_course, total_capital, 30)
    axes.plot(
        chart_manager.chart["Date"],
        invest_monthly_algorithm_result,
        label="Monthly account via algorithm",
        lw=0.5,
        color="brown",
    )

    no_invest_monthly_result = chart_manager.invest_rolling(np.repeat(1, len(chart_manager.chart)), total_capital, 30)
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
