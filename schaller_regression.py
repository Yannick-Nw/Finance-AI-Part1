from commons import *
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
chart_manager = ChartManager()

chart_manager.load("Data/MSCI GLOBAL.csv")


regression_days = 20
threshold = 0.4


r_sq = list()
signals = list()

fig, axes = plt.subplots(1, 1, num=1)

for i in range(regression_days, len(chart_manager.chart)):
    last_closes = chart_manager.chart["Close"].iloc[i - regression_days: i]
    x_values = np.array(range(regression_days)).reshape((-1, 1))
    model = LinearRegression().fit(x_values, last_closes)

    r_sq.append(model.score(x_values, last_closes))
    close_predict_prev = model.predict(np.array(regression_days - 1).reshape(-1, 1))
    close_predict_current = model.predict(np.array(regression_days).reshape(-1, 1))

    if r_sq[-1] < threshold:
        signal = 0
    else:
        signal = 1 if close_predict_current - close_predict_prev > 0 else -1
    signals.append(signal)
    if i == regression_days:
        x_points = [chart_manager.chart['Date'][0], chart_manager.chart['Date'][regression_days]]
        y_points = [model.predict(np.array(0).reshape(-1, 1)),
                    model.predict(np.array(regression_days - 1).reshape(-1, 1))]

    else:
        x_points = [chart_manager.chart['Date'][i], chart_manager.chart['Date'][i - 1]]
        y_points = [close_predict_current, close_predict_prev]

    line_color = "green" if y_points[0] - chart_manager.chart["Close"][i] > 0 else "red"
    plt.plot([x_points[0], x_points[0]], [y_points[0], chart_manager.chart["Close"][i]], color=line_color)
    plt.plot(x_points, y_points, color='yellow')

plt.plot(chart_manager.chart['Date'], chart_manager.chart["Close"], label="Closing Prices", lw=0.5, color="blue")

chart_manager.chart = chart_manager.chart.iloc[regression_days:].reset_index(drop=True)

plot_profit_fields(axes, signals, chart_manager.chart["Close"], list(chart_manager.chart["Date"]), False)





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

plot_profit_fields(axes, signals, all_in_account_values, list(chart_manager.chart["Date"]), False)



axes.xaxis.set_major_locator(mdates.YearLocator())
axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
axes.xaxis.set_minor_locator(mdates.AutoDateLocator())
axes.xaxis.set_minor_formatter(mdates.DateFormatter("%b %d"))

fig.autofmt_xdate()
fig.canvas.mpl_connect("button_release_event", update_axis_format)

plt.legend(loc="upper left")
plt.tight_layout()

fig2, ax2 = plt.subplots(1, 1, figsize=(10, 5))

ax2.plot(chart_manager.chart["Date"], r_sq, marker='o', linestyle='-')
ax2.set_title("R-Squared Values Over Time")
ax2.set_xlabel("Time Index")
ax2.set_ylabel("R-Squared Value")

plt.show()

