import numpy as np
import plotly.graph_objects as go
import humanize
from forecasting import simulate_gbm

def simulate_investment(initial_fortune,
                        years,
                        tax_rate,
                        transaction_fee=0,
                        percentace_management_fee=0,
                        ILS_management_fee=0,
                        initial_already_invested=True,
                        contributions_schedule=None,
                        forecast_params={'mu':0.07, 'sigma':0.15},
                        n_sim=100):
    """
    Simulates the evolution of an investment account over a specified number of years,
    incorporating monthly contributions, transaction fees, management fees, interest accrual,
    and taxation on profits.

    The function works as follows:
      1. It generates a full GBM forecast (with S0=1) for the simulation period using simulate_gbm.
      2. Monthly interest multipliers are computed from the GBM path by taking the ratio
         of consecutive time steps. The resulting multipliers are reshaped into a 2D array
         with dimensions [years][12], so that each month’s multiplier is accessible as:
             monthly_interest[year_idx][month_idx]
      3. The simulation loop then updates the account balance each month:
           a. A monthly contribution (with transaction fee applied) is added.
           b. Management fees are deducted—both as a monthly percentage fee (converted from an annual rate)
              and as a fixed ILS fee.
           c. The monthly interest multiplier is applied.
           d. A taxed balance is computed by reducing the profit (current balance minus total deposits)
              by the specified tax_rate.
      4. Throughout the simulation, both the untaxed and taxed monthly balances are stored.

    Parameters:
        initial_fortune (float): The starting amount in the investment account.
        years (int): The total simulation period (in years).
        tax_rate (float): Tax rate (in percent) to be applied on the profit (i.e., current balance minus total deposits).
        transaction_fee (float): Percentage fee applied to each deposit (default 0).
        percentace_management_fee (float): Annual management fee (in percent), applied monthly (default 0).
        ILS_management_fee (float): Fixed monthly management fee in ILS (default 0).
        initial_already_invested (bool): If True, the initial_fortune is assumed fully invested (thus exempt from transaction fees).
        contributions_schedule (list of lists, optional): A 2D list with dimensions [years][12] specifying the contribution amount for each month.
        forecast_params (dict): Parameters for the GBM forecast; must include 'mu' (annual drift) and 'sigma' (annual volatility).
        n_sim (int): Number of simulation paths.

    Returns:
        tuple: A tuple (paths, taxed) where:
            - paths is a NumPy array of untaxed account balances at each month (shape: (months+1, n_sim)).
            - taxed is a NumPy array of taxed account balances at each month, where tax is applied to the profit.

    Notes:
        - The function first computes market_paths using simulate_gbm. From these, it derives monthly interest multipliers as:
              monthly_interest = (market_paths[1:] / market_paths[:-1]).reshape(years, 12, -1)
          so that for each month the multiplier is available as monthly_interest[year_idx][month_idx].
        - For each month, the balance is updated by first adding the contribution (adjusted by transaction fees),
          applying management fees, and then applying the corresponding interest multiplier.
        - The taxed balance is calculated for each month as:
              taxed_balance = balances - (balances - total_deposits) * (tax_rate / 100)
          which applies tax on the gains (the difference between the current balance and the total deposits so far).
    """

    market_paths = simulate_gbm(S0=1,
                                mu=forecast_params['mu'],
                                sigma=forecast_params['sigma'],
                                T=years,
                                dt=1/12,
                                n_simulations=n_sim)

    monthly_interest = (market_paths[1:] / market_paths[:-1]).reshape(years, 12, -1)

    # Initial setup
    months = years * 12
    init_balance = initial_fortune if initial_already_invested else initial_fortune * (1 - transaction_fee / 100)
    balances = np.full(n_sim, init_balance)
    total_deposits = np.full(n_sim, initial_fortune)
    monthly_paths = [balances.copy()]
    taxed_paths = [balances.copy()]

    for m in range(1, months + 1):
        year_idx = (m - 1) // 12
        month_idx = (m - 1) % 12
        current_contribution = contributions_schedule[year_idx][month_idx]
        balances += int(current_contribution * (1 - transaction_fee / 100))  # make deposit/ withdrawal
        monthly_fee_rate = percentace_management_fee / 100 / 12
        balances = (balances * (1 - monthly_fee_rate)) - ILS_management_fee  # pay management fees
        balances = balances * monthly_interest[year_idx][month_idx]  # apply interest

        taxed_balance = balances - (balances - total_deposits) * (tax_rate / 100)
        taxed_paths.append(taxed_balance.copy())

        total_deposits += current_contribution
        monthly_paths.append(balances.copy())

    paths = np.array(monthly_paths)
    taxed = np.array(taxed_paths)
    return {
            'final_investment_paths_untaxed': paths,
            'final_investment_paths_taxed': taxed
            }

def simulate_property_value(apartment_price, years, forecast_params={'mu': 0.05, 'sigma': 0.05}, n_sim=100):
    property_paths = simulate_gbm(S0=apartment_price,
                                  mu=forecast_params['mu'],
                                  sigma=forecast_params['sigma'],
                                  T=years,
                                  dt=1/12,
                                  n_simulations=n_sim)
    return property_paths


def simulate_buying_scenario(property_value_paths,
                             mortgage,
                             years,
                             maintenance_cost_rate,
                             fixed_maintenance_cost):
    """
    Simulates the buying scenario similar to simulate_investment:
      - Uses mortgage.calc_amortization_schedule() for monthly mortgage details.
      - Uses simulate_gbm to simulate property appreciation.
      - Calculates monthly maintenance cost (variable and fixed) and accumulates it.
      - Returns summary values plus monthly paths.
    """
    total_months = years * 12

    # Obtain the mortgage amortization schedule (a list of dicts for each month)
    amortization_schedule = mortgage.amortization_schedule
    mortgage_term_months = len(amortization_schedule)

    # Initialize arrays for monthly mortgage data
    monthly_mortgage_balance = np.zeros(total_months + 1)
    monthly_interest_paid = np.zeros(total_months + 1)
    monthly_principal_paid = np.zeros(total_months + 1)

    # At month 0, the mortgage balance is the full loan amount.
    monthly_mortgage_balance[0] = mortgage.total_loan_value

    # For each month, if within the mortgage term, read the values from the schedule.
    for m in range(1, total_months + 1):
        if m <= mortgage_term_months:
            entry = amortization_schedule[m - 1]
            # Convert humanized strings to numbers
            monthly_mortgage_balance[m] = int(entry["remaining_balance"].replace(',', ''))
            monthly_interest_paid[m] = int(entry.get("interest_payment", "0").replace(',', ''))
            monthly_principal_paid[m] = int(entry.get("principal_payment", "0").replace(',', ''))
        else:
            # After the mortgage term, assume it's fully paid off.
            monthly_mortgage_balance[m] = 0
            monthly_interest_paid[m] = 0
            monthly_principal_paid[m] = 0

    n_paths = property_value_paths.shape[1]

    # Calculate monthly maintenance cost for all simulation paths.
    # Assume annual maintenance cost is: property_value * (maintenance_cost_rate/100) + fixed_maintenance_cost.
    # We then prorate it monthly.
    monthly_maintenance = np.zeros((total_months + 1, n_paths))
    monthly_cumulative_maintenance = np.zeros((total_months + 1, n_paths))
    for m in range(1, total_months + 1):
        annual_maintenance = property_value_paths[m, :] * (maintenance_cost_rate / 100) + fixed_maintenance_cost
        monthly_cost = annual_maintenance / 12
        monthly_maintenance[m, :] = monthly_cost
        monthly_cumulative_maintenance[m, :] = monthly_cumulative_maintenance[m - 1, :] + monthly_cost

    # Compute monthly net equity for all simulation paths.
    monthly_net_equity = property_value_paths - monthly_mortgage_balance[:, None] - monthly_cumulative_maintenance

    # Compute summary values from the simulation for each path.
    final_property_value = property_value_paths[-1, :]
    remaining_mortgage = monthly_mortgage_balance[-1]  # Mortgage remains the same across simulations
    total_maintenance_cost = monthly_cumulative_maintenance[-1, :]
    net_equity = monthly_net_equity[-1, :]

    return {
        'final_property_value': final_property_value,
        'remaining_mortgage': remaining_mortgage,
        'total_maintenance_cost': total_maintenance_cost,
        'net_equity': net_equity,
        'monthly_principal_paid': monthly_principal_paid,
        'monthly_interest_paid': monthly_interest_paid,
        'monthly_mortgage_balance': monthly_mortgage_balance,
        'monthly_maintenance': monthly_maintenance,
        'monthly_cumulative_maintenance': monthly_cumulative_maintenance,
        'monthly_net_equity': monthly_net_equity
    }


def plot_paths(paths, years, res=12, bins=1000, return_traces=False):
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

    if return_traces:
        return [heatmap, trace_q10, trace_q90, trace_mean]
    else:
        fig.show()
