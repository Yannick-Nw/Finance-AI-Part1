import matplotlib.pyplot as plt
import pandas as pd
from lib.Visualization.plot_stock_strategy import calculate_stock_strategy
from lib.Evalutation.compute_best_parameters import compute_best_parameters
import itertools

# Seconds needs to be higher
averages = [i for i in range(100, 200, 2)]

combos = set(itertools.combinations(averages, 2))
combos = [com for com in combos if com[1] > com[0]]
combos = [(10, 30)]
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


fig, axes = plt.subplots(1, 1, num=1)
axes.plot(
    df["firstSMA"][best_parameters[1] :].reset_index(drop=True),
    label=f"{best_parameters[0]}-day SMA",
    color="brown",
)
axes.plot(
    df["secondSMA"][best_parameters[1] :].reset_index(drop=True),
    label=f"{best_parameters[1]}-day SMA",
    color="black",
)
axes.plot(df["Close"], label="Closing Prices", lw=0.5, color="blue")

fig.legend()

start_capital = 16000
total_days = len(df)
steps = 120
start_price = df["Close"][0]
monthly_capital = start_capital / total_days * steps


fig, axes = plt.subplots(1, 1, num=2)

# Invest once
axes.plot(
    (df["Close"] / start_price) * start_capital,
    label="Invest once",
    lw=0.5,
    color="blue",
)

total_stocks = 0
monthly_investment = []
monthly_value = []
for i in range(0, total_days):
    cur_step = i // steps

    if i % steps == 0:
        total_stocks += monthly_capital / df["Close"][i]

    monthly_investment.append(monthly_capital * cur_step)
    monthly_value.append(total_stocks * df["Close"][i])

axes.plot(
    monthly_investment,
    label="Monthly investment",
    lw=0.5,
    color="green",
)
axes.plot(
    monthly_value,
    label="Invest monthly",
    lw=0.5,
    color="red",
)

algorithm_course = calculate_stock_strategy(
    axes,
    df,
)
axes.plot(
    (algorithm_course / start_price) * start_capital,
    label=f"Algorithm course invest once",
    color="purple",
)

total_stocks = 0
monthly_value = []
for i in range(0, total_days):
    cur_step = i // steps

    if i % steps == 0:
        total_stocks += monthly_capital / algorithm_course[i]

    monthly_value.append(total_stocks * algorithm_course[i])

axes.plot(
    monthly_value,
    label=f"Algorithm course invest monthly",
    color="brown",
)

fig.legend()


plt.tight_layout()
plt.show()
