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
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt

# Seconds needs to be higher
averages = [i for i in range(10, 1000, 2)]

combos = set(itertools.combinations(averages, 2))
combos = [com for com in combos if com[1] > com[0]]



# Load data
df: pd.DataFrame = pd.read_csv("Data/STOXX50E.csv", sep=",")
df = df.dropna().reset_index(drop=True)
df['Date'] = pd.to_datetime(df['Date'])

averages = dict()


def compute_strategy(df, parameters):
    df["firstSMA"] = df["Close"].rolling(window=parameters[0]).mean()
    df["secondSMA"] = df["Close"].rolling(window=parameters[1]).mean()
    df["buying"] = df["firstSMA"] < df["secondSMA"]
    return df


df, best_parameters, best_course = compute_best_parameters(df, combos, compute_strategy)

print(df)

fig, axes = plt.subplots(1, 1, num=1)

N = 100
y = np.random.rand(N)




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
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    elif range_days < 600:
        # less 600 day -> show months, days
        ax.xaxis.set_minor_locator(mdates.AutoDateLocator())
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b %d'))
    else:
        # more 600 day -> show years
        ax.xaxis.set_minor_locator(mdates.YearLocator())
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%Y'))

    fig.canvas.draw_idle()


axes.plot(
    df["Date"][best_parameters[1] :],
    df["firstSMA"][best_parameters[1] :],
    label=f"{best_parameters[0]}-day SMA",
    color="brown",
)
axes.plot(
    df["Date"][best_parameters[1]:],

    df["secondSMA"][best_parameters[1] :],
    label=f"{best_parameters[1]}-day SMA",
    color="black",
)
plt.plot( df["Date"],df["Close"], label="Closing Prices", lw=0.5, color="blue")

axes.xaxis.set_major_locator(mdates.YearLocator())
axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axes.xaxis.set_minor_locator(mdates.AutoDateLocator())
axes.xaxis.set_minor_formatter(mdates.DateFormatter('%b %d'))

fig.autofmt_xdate()
fig.canvas.mpl_connect('button_release_event', update_axis_format)


df = df.loc[best_parameters[1]:].reset_index()


start_capital = 4000
total_days = len(df)
steps = 30
start_price = df["Close"][0]
monthly_capital = start_capital / total_days * steps


plt.legend(loc="upper left")
fig, axes = plt.subplots(1, 1, num=2)

algorithm_course = calculate_stock_strategy(
    df
)
# Assuming the compute_course function and df are defined elsewhere

# Start capital
start_capital = 4000

# Monthly capital calculations
monthly_capital = start_capital / len(df) * 30  # Example calculation, adjust as necessary
steps = 30  # Assuming 'steps' is defined as part of your algorithm

# All-in account plot
all_in_account_values = compute_course(np.array(df["Close"]), start_capital)
axes.plot(
    df["Date"],
    all_in_account_values,
    label="All-in account",
    lw=0.5,
    color="blue",
)
print(f"Final amount for All-in account: {round(all_in_account_values[-1], 1)}")

# Monthly account plot
monthly_account_values = compute_course(np.array(df["Close"]), monthly_capital, steps)
axes.plot(
    df["Date"],
    monthly_account_values,
    label="Monthly account",
    lw=0.5,
    color="red",
)
print(f"Final amount for Monthly account: {round(monthly_account_values[-1], 1)}")

# All-in account via algorithm plot
alg_all_in_value = compute_course(np.array(algorithm_course), start_capital)
axes.plot(
    df["Date"],
    alg_all_in_value,
    label=f"All-in account via algorithm",
    color="purple",
)
print(f"Final amount for All-in account via algorithm: {round(alg_all_in_value[-1], 1)}")

# Monthly account via algorithm plot
monthly_account_alg_values = compute_course(np.array(algorithm_course), monthly_capital, steps)
axes.plot(
    df["Date"],
    monthly_account_alg_values,
    label=f"Monthly account via algorithm",
    color="brown",
)
print(f"Final amount for Monthly account via algorithm: {round(monthly_account_alg_values[-1], 1)}")



plot_profit_fields(axes, list(df["buying"]), alg_all_in_value, list(df["Date"]))


axes.xaxis.set_major_locator(mdates.YearLocator())
axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
axes.xaxis.set_minor_locator(mdates.AutoDateLocator())
axes.xaxis.set_minor_formatter(mdates.DateFormatter('%b %d'))

fig.autofmt_xdate()
fig.canvas.mpl_connect('button_release_event', update_axis_format)


plt.legend(loc="upper left")
plt.tight_layout()

plt.show()
