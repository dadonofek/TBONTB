import numpy as np
import plotly.graph_objects as go
import humanize
import openpyxl
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

'''
important: this file is not directly used be the main file. it is for tests and trials in the forecasting field.

Geometric Brownian Motion (GBM) is a model that simulates how stock prices evolve over time
by assuming that the continuously compounded (log) returns are normally distributed.
This means that the future price is determined by a constant average growth rate (drift)
plus a random component scaled by the stock’s volatility.

Monte Carlo simulation uses GBM by generating many random price paths to estimate the range
and probabilities of different future outcomes. In essence, it provides a statistical view 
of potential stock price scenarios, helping to quantify risks and forecast likely results.

resources:
https://www.researchgate.net/publication/384429026_Daily_and_Weekly_Geometric_Brownian_Motion_Stock_Index_Forecasts
https://www.investopedia.com/articles/07/montecarlo.asp#:~:text=One%20of%20the%20most%20common,for%20VaR%3A%20confidence%20and%20horizon
'''


def simulate_gbm(S0, mu, sigma, T, dt, n_simulations):
    """
    Simulate GBM paths.

    Parameters:
        S0 (float): Initial stock index value.
        mu (float): Annual drift (e.g. 0.07 for 7%).
        sigma (float): Annual volatility (e.g. 0.15 for 15%).
        T (float): Time horizon in years.
        dt (float): Time step in years (e.g. 1/252 for daily steps).
        n_simulations (int): Number of simulation paths.

    Returns:
        t (np.array): Array of time points.
        paths (np.array): Simulated paths (shape: n_steps x n_simulations).
    """
    n_steps = int(T / dt) + 1
    paths = np.zeros((n_steps, n_simulations))
    paths[0] = S0
    # Iterate over time steps
    for i in range(1, n_steps):
        z = np.random.standard_normal(n_simulations)  # random draws ~ N(0,1)
        paths[i] = paths[i - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
    return paths

def plot_forecast(paths, years, res=12, bins=1000, return_traces=False):
    """
    Plot an interactive heatmap of GBM simulated paths with Plotly, along with
    10th, 90th percentile lines, and the mean (median) path. The heatmap shows
    the cumulative percentage of scenarios for each bin, providing insight into
    the probability distribution of simulated outcomes.

    Parameters:
        paths (np.array): Simulated GBM paths (shape: n_steps x n_simulations).
        bins (int): Number of bins for the density heatmap.
    """
    t = np.linspace(0, years, int(years * res) + 1)
    n_simulations = paths.shape[1]
    # Calculate the 10th, 90th percentiles, and mean for each time step
    q10 = np.percentile(paths, 10, axis=1)
    q90 = np.percentile(paths, 90, axis=1)
    mean_line = np.percentile(paths, 50, axis=1)

    # Determine bins for S values across all paths
    S_min = np.min(paths)
    S_max = np.max(paths)
    bin_edges = np.linspace(S_min, S_max, bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    formatted_bin_centers = [humanize.intcomma(int(val)) for val in bin_centers]
    custom_heatmap = np.tile(formatted_bin_centers, (len(t) - 1, 1)).T
    custom_q10 = [humanize.intcomma(int(val)) for val in q10]
    custom_q90 = [humanize.intcomma(int(val)) for val in q90]
    custom_mean = [humanize.intcomma(int(val)) for val in mean_line]

    # Create a percentage density matrix for time intervals (one fewer than len(t))
    density = np.zeros((bins, len(t) - 1))
    for i in range(len(t) - 1):
        counts, _ = np.histogram(paths[i, :], bins=bin_edges, density=False)
        cum_counts = np.cumsum(counts)  # cumulative counts over the bins
        density[:, i] = (cum_counts / n_simulations) * 100  # convert to percentage

    # Create heatmap trace with custom hovertemplate
    heatmap = go.Heatmap(
        x=t[:-1],
        y=bin_centers,
        z=density,
        customdata=custom_heatmap,
        colorscale='Hot',
        colorbar=dict(title='Percentage (%)'),
        hovertemplate="Time: %{x:.2f} years<br>Index Value: %{customdata}<br>Percentage: %{z:.2f}%<extra></extra>"
    )

    # Create percentile line traces with their own hovertemplates
    trace_q10 = go.Scatter(
        x=t,
        y=q10,
        mode='lines',
        name='Pessimistic Scenario',
        line=dict(color='red', width=2),
        customdata=custom_q10,
        hovertemplate="Time: %{x:.2f} years<br>10th Percentile: %{customdata}<extra></extra>"
    )

    trace_q90 = go.Scatter(
        x=t,
        y=q90,
        mode='lines',
        name='Optimistic Scenario',
        line=dict(color='green', width=2),
        customdata=custom_q90,
        hovertemplate="Time: %{x:.2f} years<br>90th Percentile: %{customdata}<extra></extra>"
    )

    trace_mean = go.Scatter(
        x=t,
        y=mean_line,
        mode='lines',
        name='Most Likely Scenario',
        line=dict(color='blue', width=2, dash='dash'),
        customdata=custom_mean,
        hovertemplate="Time: %{x:.2f} years<br>Mean: %{customdata}<extra></extra>"
    )

    # Calculate upper bound for y-axis (90th percentile max + 10%)
    y_upper = np.max(q90) * 1.1

    fig = go.Figure(data=[heatmap, trace_q10, trace_q90, trace_mean])
    fig.update_layout(
        title='GBM Forecast Heatmap with Percentile Lines and Mean',
        xaxis_title='Time (years)',
        yaxis_title='S&P 500 Index Value',
        yaxis=dict(range=[0, y_upper]),
        legend=dict(x=0, y=1, xanchor='left', yanchor='top')
    )
    fig.show()

    if return_traces:
        return [heatmap, trace_q10, trace_q90, trace_mean]

def extract_data_from_xlsx(file_path, resolution=12):
    '''
    assumes a Central Bureau of Statistics format
    '''
    hebrew_m_to_num = {"ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4, "מאי": 5, "יוני": 6,
                            "יולי": 7, "אוגוסט": 8, "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12}
    hebrew_q_to_num = {"ינואר-מרס": 1, "אפריל-יוני": 2, "יולי-ספטמבר": 3, "אוקטובר-דצמבר": 4}
    if resolution == 12:
        hebrew_period_to_num = hebrew_m_to_num

    elif resolution == 4:
        hebrew_period_to_num = hebrew_q_to_num

    else:
        print(resolution)
        raise (f"resolution can be 4 for quarterly data or 12 for monthly data.")

    known_headers = hebrew_period_to_num.keys()

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active

    # Convert all rows to tuples of values
    rows = list(sheet.iter_rows(values_only=True))

    months_row_index = None
    months_row = None

    # identify months names row
    for i, row in enumerate(rows):
        row_values = [cell for cell in row if isinstance(cell, str)]
        if len(set(row_values) & known_headers) > 1:
            months_row_index = i
            months_row = row
            year_col = next((i for i, v in enumerate(months_row) if v == "שנה"), None)
            break


    # Collect data into a dictionary: {"YYYY-ינואר": value, ...}
    data_dict = {}
    if months_row_index is not None:
        for row in rows[months_row_index + 1:]:
            year_candidate = row[year_col]
            if year_candidate is None:
                continue
            year = int(year_candidate)
            for col_idx, month_name in enumerate(months_row[1:], start=1):
                if month_name in known_headers and col_idx < len(row):
                    val = row[col_idx]
                    if val is not None:
                        data_dict[f"{year}-{hebrew_period_to_num[month_name]}"] = val

    return data_dict

def eval_params(data):
    """
    Calculate the drift (mu) and volatility (sigma) from historical price data.

    Parameters:
      data (list or array-like): Historical data.

    Returns:
      mu (float): Mean of the log returns.
      sigma (float): Standard deviation of the log returns.
    """
    data = np.array(data)
    # Step 1: Compute log returns: r_t = ln(P_t / P_(t-1))
    log_returns = np.diff(np.log(data))
    # Step 2: Estimate parameters
    mu = np.mean(log_returns)
    sigma = np.std(log_returns, ddof=1)  # Use sample standard deviation
    return mu, sigma

def rolling_params(prices, window_years=10, data_frequency=12, start_year=1994):
    """
    Calculate annualized mu and sigma for a rolling window.

    Parameters:
        prices (list or array-like): Historical price data (assumed in time order).
        window_years (int): The length of the rolling window in years.
        data_frequency (int): Number of data points per year (e.g. 12 for monthly).
        start_year (int): The starting year of your data.

    Returns:
        times (list): The estimated year (approximate mid-point) for each window.
        mu_years (list): Annualized drift for each window.
        sigma_years (list): Annualized volatility for each window.
    """
    window_size = window_years * data_frequency
    times, mu_years, sigma_years = [], [], []
    for i in range(len(prices) - window_size + 1):
        window = prices[i : i + window_size]
        mu, sigma = eval_params(window)
        # Convert monthly parameters to yearly terms:
        mu_year = mu * data_frequency            # drift scales linearly
        sigma_year = sigma * np.sqrt(data_frequency)  # volatility scales with sqrt(time)
        mu_years.append(mu_year)
        sigma_years.append(sigma_year)
        # Use the mid-point of the window to assign a time stamp
        time_year = start_year + (i + window_size / 2) / data_frequency
        times.append(time_year)
    return times, mu_years, sigma_years

def plot_rolling_params(times, mu_years, sigma_years):
    """
    Plot the annualized drift and volatility computed from a rolling window.
    """
    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax[0].plot(times, mu_years, label='Annual Drift (mu)', color='blue')
    ax[0].set_ylabel('mu (annual)')
    ax[0].legend()
    ax[0].grid(True)

    ax[1].plot(times, sigma_years, label='Annual Volatility (sigma)', color='orange')
    ax[1].set_xlabel('Year')
    ax[1].set_ylabel('sigma (annual)')
    ax[1].legend()
    ax[1].grid(True)

    plt.tight_layout()
    plt.show()

def evaluate_gbm_params(filepath, resolution, window_years, start_year, data=None):
    if data is None:
        prices = extract_data_from_xlsx(filepath, resolution)
        prices_list = [value for value in prices.values()]
    else:
        prices_list = data

    mu, sigma = eval_params(prices_list)
    mu_year = mu * resolution
    sigma_year = sigma * np.sqrt(resolution)
    print(f'entire term {mu_year = }')
    print(f'entire term {sigma_year = }')

    times, mu_years, sigma_years = rolling_params(prices_list,
                                                  window_years=window_years,
                                                  data_frequency=resolution,
                                                  start_year=start_year)
    plot_rolling_params(times, mu_years, sigma_years)

if __name__ == "__main__":
    # # Example parameters from Sinha's article for SP500:
    # S0 = 1  # Initial value
    # mu = 0.078  # 7% annual drift
    # sigma = 0.15  # 15% annual volatility
    # T = 30  # Forecast horizon of 30 years
    # dt = 1 / 12  # Monthly time steps
    # n_simulations = 10000  # Number of simulation paths
    #
    # paths = simulate_gbm(S0, mu, sigma, T, dt, n_simulations)
    # plot_forecast(paths, years=T)

    evaluate_gbm_params(filepath='data/IL_hous_prices_quarterly_2017_2024.xlsx',
                        resolution=4,
                        window_years=3,
                        start_year=2017)


    # findings so far
    # index says:
        # mu_apt = 5.7
        # sigma_apt = 3.5
    # prices_q says:
        # mu_apt = 5.4
        # sigma_apt = 5.2
    # haifa_3_4 says:
        # mu_apt = 5.2
        # sigma_apt = 5.6

    # # Download daily data from 1950 onward (this is the longest reliable period from Yahoo Finance)
    # sp500 = yf.download("^GSPC", start="1950-01-01")
    # first_day = sp500.groupby(sp500.index.to_period("M")).first()
    # sp500_prices_list = first_day["Close"].squeeze().to_numpy().astype(int).tolist()
    #
    # evaluate_gbm_params(filepath='',
    #                     resolution=12,
    #                     window_years=30,
    #                     start_year=1950,
    #                     data=sp500_prices_list)
