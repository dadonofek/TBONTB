import numpy as np
import plotly.graph_objects as go
import humanize

'''
important: this file is not directly used be the main file. it is for tests and trials in the forecasting field.
Geometric Brownian Motion (GBM) is a model that simulates how stock prices evolve over time
by assuming that the continuously compounded (log) returns are normally distributed.
This means that the future price is determined by a constant average growth rate (drift)
plus a random component scaled by the stock’s volatility.

Monte Carlo simulation uses GBM by generating many random price paths to estimate the range
and probabilities of different future outcomes. In essence, it provides a statistical view 
of potential stock price scenarios, helping to quantify risks and forecast likely results.

For more details, see Sinha’s article here:
https://www.researchgate.net/publication/384429026_Daily_and_Weekly_Geometric_Brownian_Motion_Stock_Index_Forecasts
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
        t (np.array): Time array.
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


if __name__ == "__main__":
    # Example parameters from Sinha's article:
    S0 = 1  # Initial value
    mu = 0.07  # 7% annual drift
    sigma = 0.15  # 15% annual volatility
    T = 30  # Forecast horizon of 30 years
    dt = 1 / 12  # Monthly time steps
    n_simulations = 10000  # Number of simulation paths

    paths = simulate_gbm(S0, mu, sigma, T, dt, n_simulations)
    plot_forecast(paths, years=T)
