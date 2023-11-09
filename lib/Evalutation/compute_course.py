def compute_course(course, investment, steps=None):
    total_days = len(course)
    if not steps:
        return (course / course[0]) * investment
    alg_total_stocks = 0
    alg_monthly_value = []
    for i in range(0, total_days):
        if i % steps == 0:
            alg_total_stocks += investment / course[i]
        alg_monthly_value.append(alg_total_stocks * course[i])

    return alg_monthly_value
