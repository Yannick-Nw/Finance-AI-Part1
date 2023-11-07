"""
Usage:

df.readinStock

df["buying"] = df["firstSMA"] < df['secondSMA']

def function_to_plot():
    plt.plot(df['firstSMA'][higher_averages[0]:].reset_index(drop=True), label=f'{lower_average}-day SMA', color='red')
    plt.plot(df['secondSMA'][higher_averages[0]:].reset_index(drop=True), label=f'{higher_average}-day SMA', color='black')


plot_stock_strategy(df[higher_average:].reset_index(drop=True), function_to_plot)
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates


def _plot_entry(index, stock_entry, total_screen_height, total_screen_width, ax):
    """
    index (int): The index of the stock entry.
    stock_entry (dict): A dictionary containing stock data for a particular day. It should have keys "Close" (closing price) and "buying" (a boolean indicating whether a stock is being bought).
    total_screen_height (float): The difference between the first and the last closing prices in the dataset.
    total_screen_width (float): The total width of the screen/plot.
    """
    arrow_length = total_screen_height / 4

    head_length = arrow_length / 16
    head_width = total_screen_width / 200
    if stock_entry["buying"]:
        ax.arrow(index, stock_entry['Close'] + arrow_length, 0, -arrow_length + head_length,
                  head_width=head_width, head_length=head_length, fc='green', ec='green')
    else:
        ax.arrow(index, stock_entry['Close'] - arrow_length, 0, arrow_length - head_length,
                  head_width=head_width, head_length=head_length, fc='red', ec='red')


def plot_stock_strategy(df, function_to_plot=None, num_of_stocks=10, invest_per_month=100):
    """
    df (DataFrame): A pandas DataFrame containing stock data.
    It should have columns "Close" (closing prices) and "buying" (boolean values indicating whether a
    stock is being bought on a particular day).

    function_to_plot (function, optional): An optional function to plot the custom strategy.
    """
    fig, axes = plt.subplots(1, 3)


    plt.subplots_adjust(wspace=0)
    axes[0].set_title('Stock Course with strategy')
    axes[1].set_title(f'Strategy while always buying {num_of_stocks} stock(s)')
    axes[2].set_title(f'Strategy while investing {invest_per_month} $ per month')

    for ax in axes:
        ax.set_xlabel('Days')
        ax.set_ylabel('$')


    if function_to_plot is not None:
        function_to_plot(axes[0])

    axes[0].plot(df['Close'], label='Closing Prices', color='blue')

    total_screen_height = abs(df["Close"][0] - df["Close"][len(df) - 1])

    df_iter = df.iterrows()
    index, stock_entry = next(df_iter)
    _plot_entry(index, stock_entry, total_screen_height, len(df), axes[0])
    algorithm_course = [stock_entry["Close"]]

    buying_per_month = {"course": [stock_entry["Close"]], "invested_money": 0, "uninvested_money": invest_per_month}
    for i, stock_entry in df_iter:
        # Sell when there is a change. There is one day where you still buy while buying is false
        # this is because you could not have known that the change will come tomorrow so you have to hold it until
        # a change comes.
        # Because we are adding the last day we are always one day behind
        if stock_entry["buying"] and df["buying"][i - 1] or not stock_entry["buying"] and df["buying"][i - 1]:
            algorithm_course.append(algorithm_course[-1] + (stock_entry["Close"] - df["Close"][i - 1]))
            buying_per_month["course"].append(algorithm_course[-1] + (stock_entry["Close"] - df["Close"][i - 1]))

        else:
            algorithm_course.append(algorithm_course[-1])

        if stock_entry["buying"] != df["buying"][i - 1]:
            _plot_entry(i, stock_entry, total_screen_height, len(df), axes[0])

        # Investing per month


    axes[0].plot(algorithm_course, label=f'Algorithm course', color='purple')
    axes[1].plot(np.array(algorithm_course) * num_of_stocks, label=f'Algorithm course', color='green')

    plt.tight_layout()
    plt.show()

