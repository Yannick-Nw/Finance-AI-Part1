import matplotlib.pyplot as plt
import pandas as pd
from lib.Visualization.plot_stock_strategy import (
    calculate_stock_strategy,
    plot_profit_fields,
)
from lib.Evalutation.compute_best_parameters import compute_best_parameters
import itertools

# Seconds needs to be higher
averages = [i for i in range(10, 250, 2)]

combos = set(itertools.combinations(averages, 2))
combos = [com for com in combos if com[1] > com[0]]

# Load data
df: pd.DataFrame = pd.read_csv("Data/MSCI GLOBAL.csv", sep=",")
df = df.dropna().reset_index(drop=True)
averages = dict()


def compute_strategy(df, parameters):
    df["firstSMA"] = df["Close"].rolling(window=parameters[0]).mean()
    df["secondSMA"] = df["Close"].rolling(window=parameters[1]).mean()
    df["buying"] = df["firstSMA"] < df["secondSMA"]
    return df


df, best_parameters, best_course = compute_best_parameters(df, combos, compute_strategy)
print(best_parameters)

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

# Invest once

total_stocks = 0
monthly_value = []
for i in range(0, total_days):
    cur_step = i // steps

    if i % steps == 0:
        total_stocks += monthly_capital / df["Close"][i]

    monthly_value.append(total_stocks * df["Close"][i])

algorithm_course = calculate_stock_strategy(
    axes,
    df,
)

alg_total_stocks = 0
alg_monthly_value = []
for i in range(0, total_days):
    cur_step = i // steps

    if i % steps == 0:
        alg_total_stocks += monthly_capital / algorithm_course[i]

    alg_monthly_value.append(alg_total_stocks * algorithm_course[i])

all_in_value = (df["Close"] / start_price) * start_capital
alg_all_in_value = (algorithm_course / start_price) * start_capital

axes.plot(
    all_in_value,
    label="All-in account",
    lw=0.5,
    color="blue",
)
axes.plot(
    monthly_value,
    label="Monthly account",
    lw=0.5,
    color="red",
)
axes.plot(
    alg_all_in_value,
    label=f"All-in account via algorithm",
    color="purple",
)
axes.plot(
    alg_monthly_value,
    label=f"Monthly account via algorithm",
    color="brown",
)
plot_profit_fields(axes, list(df["buying"]), list(alg_all_in_value))

monthly_investment = []
for i in range(0, total_days):
    monthly_investment.append(monthly_capital * (i // steps))

axes.plot(
    monthly_investment,
    label="Capital of monthly account",
    lw=0.5,
    color="green",
    alpha=0.5,
)

plt.legend(loc="upper left")
plt.ticklabel_format(style="plain")
plt.tight_layout()
plt.show()
