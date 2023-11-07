"""
Usage:

df.readinStock

df["buying"] = df["firstSMA"] < df['secondSMA']

def function_to_plot():
    plt.plot(df['firstSMA'][higher_averages[0]:].reset_index(drop=True), label=f'{lower_average}-day SMA', color='red')
    plt.plot(df['secondSMA'][higher_averages[0]:].reset_index(drop=True), label=f'{higher_average}-day SMA', color='black')


plot_stock_strategy(df[higher_average:].reset_index(drop=True), function_to_plot)
"""

import math
from matplotlib import figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame


def plot_profit_fields(ax: Axes, buying_list: list[bool], chart: list[float]):
    last_action_entry = (0, chart[0])
    for i, to_buy in enumerate(buying_list[1:]):
        if to_buy != buying_list[i - 1]:
            last_index, last_entry = last_action_entry
            if not to_buy:
                _plot_entry(ax, last_index, i, last_entry, chart[i])
            last_action_entry = (i, chart[i])


def _plot_entry(
    ax: Axes,
    first_index,
    second_index,
    first_entry,
    second_entry,
):
    """
    index (int): The index of the stock entry.
    stock_entry (dict): A dictionary containing stock data for a particular day. It should have keys "Close" (closing price) and "buying" (a boolean indicating whether a stock is being bought).
    total_screen_height (float): The difference between the first and the last closing prices in the dataset.
    total_screen_width (float): The total width of the screen/plot.
    """

    color = "red" if second_entry < first_entry else "green"
    ax.fill_betweenx(
        [0, max(first_entry, second_entry)],
        first_index,
        second_index,
        facecolor=color,
        alpha=0.3,
    )


def calculate_stock_strategy(axes: Axes, df, invest_per_month=100):
    """
    df (DataFrame): A pandas DataFrame containing stock data.
    It should have columns "Close" (closing prices) and "buying" (boolean values indicating whether a
    stock is being bought on a particular day).
    """
    axes.set_title("Stock Course with strategy")
    axes.set_xlabel("Days")
    axes.set_ylabel("$")

    total_screen_height = abs(df["Close"][0] - df["Close"][len(df) - 1])

    df_iter = df.iterrows()
    index, stock_entry = next(df_iter)
    algorithm_course = [stock_entry["Close"]]

    buying_per_month = {
        "course": [stock_entry["Close"]],
        "invested_money": 0,
        "uninvested_money": invest_per_month,
    }
    last_action_entry = (index, stock_entry)
    for i, stock_entry in df_iter:
        # Sell when there is a change. There is one day where you still buy while buying is false
        # this is because you could not have known that the change will come tomorrow so you have to hold it until
        # a change comes.
        # Because we are adding the last day we are always one day behind
        if (
            stock_entry["buying"]
            and df["buying"][i - 1]
            or not stock_entry["buying"]
            and df["buying"][i - 1]
        ):
            algorithm_course.append(
                algorithm_course[-1] + (stock_entry["Close"] - df["Close"][i - 1])
            )
            buying_per_month["course"].append(
                algorithm_course[-1] + (stock_entry["Close"] - df["Close"][i - 1])
            )
        else:
            algorithm_course.append(algorithm_course[-1])

        if stock_entry["buying"] != df["buying"][i - 1]:
            last_index, last_entry = last_action_entry
            # _plot_entry(
            #     last_index,
            #     i,
            #     last_entry,
            #     stock_entry,
            #     total_screen_height,
            #     len(df),
            #     axes,
            # )
            # last_action_entry = (i, stock_entry)

    return algorithm_course
