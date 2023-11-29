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
#from lib.Visualization.plot_stock_strategy import plot_profit_fields



def run():
    # Load data
    chart_manager = ChartManager()
    chart_manager.load("Data/MSCI GLOBAL.csv")

    window_size = 24
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
    Plot investing results
    """
    signals = [0] * len(chart_manager.chart)
    out_of_bands = False
    long_buy_points = []
    long_sell_points = []
    short_buy_points = []
    short_sell_points = []

    for i in range(1, len(chart_manager.chart)):
        current_close = chart_manager.chart['Close'].iloc[i]
        previous_close = chart_manager.chart['Close'].iloc[i-1]
        current_lowest_price = chart_manager.chart['Low'].iloc[i]
        current_highest_price = chart_manager.chart['High'].iloc[i]
        previous_highest_price = chart_manager.chart['High'].iloc[i-1]
        previous_lowest_price = chart_manager.chart['Low'].iloc[i - 1]
        lower_band = lower_band_data.iloc[i]
        upper_band = upper_band_data.iloc[i]
        current_ma = ma_data.iloc[i]
        previous_ma = ma_data.iloc[i - 1]
        
        
        if out_of_bands == True and (current_close > upper_band or current_close < lower_band) and signals[i-1]==0:
            continue
        elif out_of_bands == True and previous_highest_price > upper_band and current_close < upper_band:
            signals[i] = -1
            short_buy_points.append(i)
            out_of_bands = False
            continue
        elif out_of_bands == True and previous_lowest_price > lower_band and current_close > lower_band:
            signals[i] = 1
            long_buy_points.append(i)
            out_of_bands = False
            continue

        """
        Long signals
        """
        if previous_close < current_ma and current_close > current_ma and signals[i-1] == 0:
            signals[i] = 1
            long_buy_points.append(i)
            continue
        
        if signals[i - 1] == 1:
            # Verkaufssignal für Long-Position
            if current_highest_price > upper_band:
                signals[i] = 0
                long_sell_points.append(i)
                out_of_bands = True
                continue
            # Verkaufssignal für Long-Position
            elif previous_lowest_price > previous_ma and current_close < current_ma:
                signals[i] = -1
                long_sell_points.append(i)
                short_buy_points.append(i)
                continue

        """
        Short signals
        """
        # Short-Signal: Schneidet MA von oben
        if previous_lowest_price > current_ma and current_close < current_ma and signals[i-1] == 0:
            signals[i] = -1
            short_buy_points.append(i)
            continue
        
        # Verkaufssignal für Short-Position
        if signals[i - 1] == -1:
            if current_lowest_price < lower_band:
                signals[i] = 0
                short_sell_points.append(i)
                out_of_bands = True
                continue
            if previous_highest_price < previous_ma and current_close > current_ma:
                signals[i] = 1
                short_sell_points.append(i)
                long_buy_points.append(i)
                continue

        signals[i] = signals[i - 1]
  
    algorithm_course = chart_manager.calculate_return(signals)

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

    # Pfeile hinzufügen
    for index in long_buy_points:
        plt.annotate('', xy=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index]), 
                    xytext=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index] - 2), 
                    arrowprops=dict(edgecolor='green', arrowstyle='->'))

    for index in long_sell_points:
        plt.annotate('', xy=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index]), 
                    xytext=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index] + 2), 
                    arrowprops=dict(edgecolor='red', arrowstyle='->'))
    
    for index in short_buy_points:
        plt.annotate('', xy=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index]), 
                    xytext=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index] - 2), 
                    arrowprops=dict(edgecolor='blue', arrowstyle='->'))
    
    for index in short_sell_points:
        plt.annotate('', xy=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index]), 
                    xytext=(chart_manager.chart['Date'].iloc[index], chart_manager.chart['Close'].iloc[index] + 2), 
                    arrowprops=dict(edgecolor='orange', arrowstyle='->'))


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
