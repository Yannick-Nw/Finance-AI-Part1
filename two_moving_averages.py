import pandas as pd
from lib.Visualization.plot_stock_strategy import plot_stock_strategy
from lib.Evalutation.compute_best_parameters import compute_best_parameters
import itertools

# Seconds needs to be higher
averages = [i for i in range(100, 200, 2)]

combos = set(itertools.combinations(averages, 2))
combos = [com for com in combos if com[1] > com[0]]

# Load data
df = pd.read_csv('Data/MSCI GLOBAL.csv', sep=',')
averages = dict()


def compute_strategy(df, parameters):
    df['firstSMA'] = df['Close'].rolling(window=parameters[0]).mean()
    df['secondSMA'] = df['Close'].rolling(window=parameters[1]).mean()
    df["buying"] = df["firstSMA"] < df['secondSMA']
    return df


df, best_parameters, best_course = compute_best_parameters(df,
                                                           combos,
                                                           compute_strategy)

def function_to_plot(axes):
    axes.plot(df['firstSMA'][best_parameters[1]:].reset_index(drop=True), label=f'{best_parameters[0]}-day SMA', color='brown')
    axes.plot(df['secondSMA'][best_parameters[1]:].reset_index(drop=True), label=f'{best_parameters[1]}-day SMA',
             color='black')


plot_stock_strategy(df[best_parameters[1]:].reset_index(drop=True), function_to_plot)

