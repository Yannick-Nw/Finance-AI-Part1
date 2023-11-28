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

    window_size = 40
    #14-Tage MA
    ma_data = chart_manager.chart['Close'].rolling(window=window_size).mean()
    #14-Tage-Standardabweichung
    std_data = chart_manager.chart['Close'].rolling(window=window_size).std()
    #Obere Bollinger-Band
    upper_band_data = ma_data + (std_data * 2)
    #Untere Bollinger-Band
    lower_band_data = ma_data - (std_data * 2)

    # So that the chart only starts when indicator is valid
    shift_n = ma_data.first_valid_index()

    chart_manager.chart = chart_manager.chart.iloc[shift_n:].reset_index(drop=True)
    ma_data = ma_data.iloc[shift_n:].reset_index(drop=True)
    std_data = std_data.iloc[shift_n:].reset_index(drop=True)
    upper_band_data = upper_band_data.iloc[shift_n:].reset_index(drop=True)
    lower_band_data = lower_band_data.iloc[shift_n:].reset_index(drop=True)

    """
    Plot indicators with chart
    """
    axes: Axes  # Needed for intellisense
    fig, axes = plt.subplots(1, 1, num=1)

    axes.plot(
        chart_manager.chart["Date"], ma_data, label=f"Moving Average ({window_size})", lw=0.5, color="orange"
    )
    axes.plot(
        chart_manager.chart["Date"], upper_band_data, label=f"Upper Band ({window_size})", lw=0.5, color="red"
    )
    axes.plot(
        chart_manager.chart["Date"], lower_band_data, label=f"Lower Band ({window_size})", lw=0.5, color="green"
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
    signals = [0] * len(chart_manager.chart)

    for i in range(1, len(chart_manager.chart)):
        current_close = chart_manager.chart['Close'].iloc[i]
        previous_close = chart_manager.chart['Close'].iloc[i - 1]
        current_ma = ma_data.iloc[i]
        previous_ma = ma_data.iloc[i - 1]
        
        """
        Long signals
        """
        if previous_close <= previous_ma and current_close >= current_ma and (current_close-previous_close)>=previous_close/100 and signals[i] == 0:
            signals[i] = 1
            continue
        
        if signals[i - 1] == 1:
            # Verkaufssignal für Long-Position
            if current_close > upper_band_data.iloc[i]:
                signals[i] = 0
                continue
            # Verkaufssignal für Long-Position
            elif current_close < current_ma:
                signals[i] = -1
                continue

        """
        Short signals
        """
        # Short-Signal: Schneidet MA von oben
        if previous_close >= previous_ma and current_close <= current_ma and signals[i] == 0:
            signals[i] = -1
            continue
        
        # Verkaufssignal für Short-Position
        if signals[i - 1] == -1:
            if current_close < lower_band_data.iloc[i]:
                signals[i] = 0
                continue
            if current_close > current_ma:
                signals[i] = 1
                continue

        signals[i] = signals[i - 1]
        
    algorithm_course = chart_manager.calculate_return(signals)

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

    plot_profit_fields(axes, signals, invest_once_algorithm_result, chart_manager.chart["Date"])

    print(f"""
Final amount for All-in account: {round(invest_once_result[-1], 1)} $
Final amount for All-in account via algorithm: {round(invest_once_algorithm_result[-1], 1)} $
Final amount for Monthly account: {round(invest_monthly_result[-1], 1)} $
Final amount for Monthly account via algorithm: {round(invest_monthly_algorithm_result[-1], 1)} $
Final amount for just saving: {round(no_invest_monthly_result[-1], 1)} $
""")
    
    axes.plot(
        chart_manager.chart["Date"], ma_data / ma_data.iloc[0] * (total_capital * (ma_data.iloc[0] / chart_manager.chart['Close'].iloc[0])), label=f"Moving Average ({window_size})", lw=0.5, color="orange"
    )
    axes.plot(
        chart_manager.chart["Date"], upper_band_data / upper_band_data.iloc[0] * (total_capital * (upper_band_data.iloc[0] / chart_manager.chart['Close'].iloc[0])), label=f"Upper Band ({window_size})", lw=0.5, color="red"
    )
    axes.plot(
        chart_manager.chart["Date"], lower_band_data / lower_band_data.iloc[0] * (total_capital * (lower_band_data.iloc[0] / chart_manager.chart['Close'].iloc[0])), label=f"Lower Band ({window_size})", lw=0.5, color="green"
    )

    axes.xaxis.set_major_locator(mdates.YearLocator())
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes.xaxis.set_minor_locator(mdates.AutoDateLocator())
    axes.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))

    plt.legend(loc="upper left")
    plt.show()

    

if __name__ == "__main__":
    run()
