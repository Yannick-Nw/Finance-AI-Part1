import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from Visualization.plot_stock_strategy import plot_stock_strategy

def get_percentage(low, difference):
    return difference / low * 100


# Seconds needs to be higher
lower_averages = [500]
higher_averages = [520]

# Always start at the highest to save the same timeframe
highest = max(higher_averages)

# Load data
df = pd.read_csv('Data/MSCI GLOBAL.csv', sep=',')
averages = dict()

for lower_average, higher_average in tqdm(zip(lower_averages, higher_averages) ,total=len(lower_averages)):
    df['firstSMA'] = df['Close'].rolling(window=lower_average).mean()
    df['secondSMA'] = df['Close'].rolling(window=higher_average).mean()
    balance = 0
    buy = 0
    buying = False

    df["buying"] = df["firstSMA"] < df['secondSMA']

def function_to_plot():
    plt.plot(df['firstSMA'][higher_averages[0]:].reset_index(drop=True), label=f'{lower_average}-day SMA', color='red')
    plt.plot(df['secondSMA'][higher_averages[0]:].reset_index(drop=True), label=f'{higher_average}-day SMA', color='black')


plot_stock_strategy(df[higher_average:].reset_index(drop=True), function_to_plot)

