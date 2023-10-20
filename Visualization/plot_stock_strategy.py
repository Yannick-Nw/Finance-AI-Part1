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


def _plot_entry(index, stock_entry, total_screen_height, total_screen_width):
    """
    index (int): The index of the stock entry.
    stock_entry (dict): A dictionary containing stock data for a particular day. It should have keys "Close" (closing price) and "buying" (a boolean indicating whether a stock is being bought).
    total_screen_height (float): The difference between the first and the last closing prices in the dataset.
    total_screen_width (float): The total width of the screen/plot.
    """
    arrow_length = total_screen_height / 4

    head_length = arrow_length / 4
    head_width = total_screen_width / 200
    if stock_entry["buying"]:
        plt.arrow(index, stock_entry['Close'] + arrow_length, 0, -arrow_length + head_length,
                  head_width=head_width, head_length=head_length, fc='green', ec='green')
    else:
        plt.arrow(index, stock_entry['Close'] - arrow_length, 0, arrow_length - head_length,
                  head_width=head_width, head_length=head_length, fc='red', ec='red')


def plot_stock_strategy(df, function_to_plot=None):
    """
    df (DataFrame): A pandas DataFrame containing stock data.
    It should have columns "Close" (closing prices) and "buying" (boolean values indicating whether a
    stock is being bought on a particular day).

    function_to_plot (function, optional): An optional function that can be plotted before plotting the stock data.
    """
    plt.figure(figsize=(12, 6))
    if function_to_plot is not None:
        function_to_plot()
    plt.plot(df['Close'], label='Closing Prices', color='blue')

    total_screen_height = abs(df["Close"][0] - df["Close"][len(df) - 1])

    df_iter = df.iterrows()
    index, stock_entry = next(df_iter)
    _plot_entry(index, stock_entry, total_screen_height, len(df))
    algorithm_course = [stock_entry["Close"]]

    for i, stock_entry in df_iter:
        if stock_entry["buying"]:
            algorithm_course.append(algorithm_course[-1] + (stock_entry["Close"] - df["Close"][i - 1]))
        else:
            algorithm_course.append(algorithm_course[-1])

        if stock_entry["buying"] != df["buying"][i - 1]:
            _plot_entry(i, stock_entry, total_screen_height, len(df))

    plt.plot(algorithm_course, label=f'Algorithm course', color='green')
    plt.title('Closing Prices two Moving Average')
    plt.legend()
    plt.show()

