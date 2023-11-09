import matplotlib.pyplot as plt
import pandas as pd
from lib.Visualization.plot_stock_strategy import (
    calculate_stock_strategy,
    plot_profit_fields,
)
from lib.Evalutation.compute_best_parameters import compute_best_parameters
from lib.Evalutation.compute_course import compute_course
import numpy as np
import itertools

# Seconds needs to be higher
averages = [i for i in range(10, 1000, 2)]

combos = set(itertools.combinations(averages, 2))
combos = [com for com in combos if com[1] > com[0]]

combos = [(234, 482)]

# Load data
df: pd.DataFrame = pd.read_csv("Data/STOXX50E.csv", sep=",")
df = df.dropna().reset_index(drop=True)
averages = dict()


def compute_strategy(df, parameters):
    df["firstSMA"] = df["Close"].rolling(window=parameters[0]).mean()
    df["secondSMA"] = df["Close"].rolling(window=parameters[1]).mean()
    df["buying"] = df["firstSMA"] < df["secondSMA"]
    return df


df, best_parameters, best_course = compute_best_parameters(df, combos, compute_strategy)

fig, axes = plt.subplots(1, 1, num=1)
axes.plot(
    df["firstSMA"][best_parameters[1] :],
    label=f"{best_parameters[0]}-day SMA",
    color="brown",
)
axes.plot(
    df["secondSMA"][best_parameters[1] :],
    label=f"{best_parameters[1]}-day SMA",
    color="black",
)
axes.plot(df["Close"], label="Closing Prices", lw=0.5, color="blue")


start_capital = 4000
total_days = len(df)
steps = 30
start_price = df["Close"][0]
monthly_capital = start_capital / total_days * steps


plt.legend(loc="upper left")
plt.ticklabel_format(style="plain")
fig, axes = plt.subplots(1, 1, num=2)

algorithm_course = calculate_stock_strategy(
    df,
)
axes.plot(
    compute_course(np.array(df["Close"]), start_capital),
    label="All-in account",
    lw=0.5,
    color="blue",
)
axes.plot(
    compute_course(np.array(df["Close"]), monthly_capital, steps),
    label="Monthly account",
    lw=0.5,
    color="red",
)
alg_all_in_value = compute_course(np.array(algorithm_course), start_capital)
axes.plot(
    alg_all_in_value,
    label=f"All-in account via algorithm",
    color="purple",
)

axes.plot(
    compute_course(np.array(algorithm_course), monthly_capital, steps),
    label=f"Monthly account via algorithm",
    color="brown",
)

plot_profit_fields(axes, list(df["buying"]), alg_all_in_value)

axes.plot(
    compute_course(np.ones(len(df["Close"])), monthly_capital, steps),
    label="Capital of monthly account",
    lw=0.5,
    color="green",
    alpha=0.5,
)

plt.legend(loc="upper left")
plt.ticklabel_format(style="plain")
plt.tight_layout()
plt.show()
