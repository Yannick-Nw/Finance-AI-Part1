import matplotlib.pyplot as plt
import pandas as pd
from commons import *
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt


def run():
    chart_manager = ChartManager()
    # Seconds needs to be higher
    averages = [i for i in range(10, 100, 2)]

    combos = set(itertools.combinations(averages, 2))
    combos = [com for com in combos if com[1] > com[0]]
    # Load data
    chart_manager.load("Data/STOXX50E.csv")

    def compute_strategy(df, parameters):
        df["firstSMA"] = df["Close"].rolling(window=parameters[0]).mean()
        df["secondSMA"] = df["Close"].rolling(window=parameters[1]).mean()
        df["buying"] = df["firstSMA"] < df["secondSMA"]
        return df

    best_parameters = compute_best_parameters(
        chart_manager.chart, combos, compute_strategy
    )
    shift_n = best_parameters[1]

    first_sma = chart_manager.chart["Close"].rolling(window=best_parameters[0]).mean()
    second_sma = chart_manager.chart["Close"].rolling(window=best_parameters[1]).mean()

    first_sma = first_sma.iloc[shift_n:].reset_index(drop=True)
    second_sma = second_sma.iloc[shift_n:].reset_index(drop=True)

    signals = np.where(
        first_sma < second_sma,
        100,
        -100
    )

    chart_manager.chart = chart_manager.chart.iloc[shift_n:].reset_index(drop=True)



    fig, axes = plt.subplots(1, 1, num=1)

    def update_axis_format(event):
        ax = event.inaxes

        try:
            xlim = ax.get_xlim()
        except AttributeError:
            return
        start, end = mdates.num2date(xlim[0]), mdates.num2date(xlim[1])
        range_days = (end - start).days
        if range_days < 30:
            # less 30 day -> show days
            ax.xaxis.set_minor_locator(mdates.DayLocator())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
        elif range_days < 600:
            # less 600 day -> show months, days
            ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))
        else:
            # more 600 day -> show years
            ax.xaxis.set_minor_locator(mdates.YearLocator())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%Y"))

        fig.canvas.draw_idle()

    axes.plot(
        chart_manager.chart["Date"],
        first_sma,
        label=f"{best_parameters[0]}-day SMA",
        color="brown",
    )
    axes.plot(
        chart_manager.chart["Date"],
        second_sma,
        label=f"{best_parameters[1]}-day SMA",
        color="black",
    )
    plt.plot(chart_manager.chart["Date"], chart_manager.chart["Close"], label="Closing Prices", lw=0.5, color="blue")

    axes.xaxis.set_major_locator(mdates.YearLocator())
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes.xaxis.set_minor_locator(mdates.AutoDateLocator())
    axes.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))

    fig.autofmt_xdate()
    fig.canvas.mpl_connect("button_release_event", update_axis_format)

    plt.legend(loc="upper left")
    fig, axes = plt.subplots(1, 1, num=2)

    algorithm_course = chart_manager.calculate_return(signals)
    # Assuming the compute_course function and df are defined elsewhere

    # Start capital
    start_capital = 4000

    # Monthly capital calculations
    steps = 30

    monthly_capital = start_capital / len(chart_manager.chart) * steps


    # All-in account plot
    all_in_account_values = chart_manager.invest_once(np.array(chart_manager.chart["Close"]), start_capital)
    axes.plot(
        chart_manager.chart["Date"],
        all_in_account_values,
        label="All-in account",
        lw=0.5,
        color="blue",
    )
    print(f"Final amount for All-in account: {round(all_in_account_values[-1], 1)}")

    # Monthly account plot
    monthly_account_values = chart_manager.invest_rolling(
        np.array(chart_manager.chart["Close"]), 0, monthly_capital, steps
    )
    axes.plot(
        chart_manager.chart["Date"],
        monthly_account_values,
        label="Monthly account",
        lw=0.5,
        color="red",
    )
    print(f"Final amount for Monthly account: {round(monthly_account_values[-1], 1)}")

    # All-in account via algorithm plot

    alg_all_in_value = chart_manager.invest_once(np.array(algorithm_course), start_capital)
    axes.plot(
        chart_manager.chart["Date"],
        alg_all_in_value,
        label=f"All-in account via algorithm",
        color="purple",
    )
    print(
        f"Final amount for All-in account via algorithm: {round(alg_all_in_value[-1], 1)}"
    )

    # Monthly account via algorithm plot
    monthly_account_alg_values = chart_manager.invest_rolling(
        np.array(algorithm_course), 0, monthly_capital, steps
    )
    axes.plot(
        chart_manager.chart["Date"],
        monthly_account_alg_values,
        label=f"Monthly account via algorithm",
        color="brown",
    )
    print(
        f"Final amount for Monthly account via algorithm: {round(monthly_account_alg_values[-1], 1)}"
    )


    plot_profit_fields(axes, signals, alg_all_in_value, list(chart_manager.chart["Date"]))

    axes.xaxis.set_major_locator(mdates.YearLocator())
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes.xaxis.set_minor_locator(mdates.AutoDateLocator())
    axes.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))

    fig.autofmt_xdate()
    fig.canvas.mpl_connect("button_release_event", update_axis_format)

    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    run()
