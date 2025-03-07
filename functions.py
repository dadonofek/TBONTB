import numpy as np
import plotly.graph_objects as go
import humanize

def generate_interest_schedule(initial_rate, mu, theta, sigma, years):
# thoughts: evaluate real world params and use.
    """
    Generates a 2D interest schedule (annual rates in percent) using the Ornstein–Uhlenbeck process.

    Parameters:
        initial_rate: Initial annual interest rate (in percent).
        mu: Long-run mean annual interest rate (in percent).
        theta: Speed of mean reversion.
        sigma: Volatility (in percent).
        years: Number of years to simulate.

    Returns:
        A 2D list of simulated monthly interest rates (in percent) with dimensions [years][12].
    """
    dt = 1 / 12  # time step for one month
    schedule = []
    rate = initial_rate
    for _ in range(years):
        year_rates = []
        for _ in range(12):
            # Increment from the Ornstein–Uhlenbeck process:
            dW = np.random.normal(0, np.sqrt(dt))
            rate = rate + theta * (mu - rate) * dt + sigma * dW
            # Optionally, ensure the rate doesn't go negative:
            rate = max(rate, 0)
            year_rates.append(rate)
        schedule.append(year_rates)
    return schedule

def simulate_investment(initial_fortune,
                        monthly_contribution,
                        years,
                        tax_rate,
                        transaction_fee=0,
                        percentace_management_fee=0,
                        ILS_management_fee=0,
                        initial_already_invested=True,
                        contributions_schedule=None,
                        forecast_params={'mu':0.07, 'sigma':0.15, 'dt':1/12},
                        n_sim=100):
    """
    Simulates the growth of an investment over a number of years with variable contributions,
    fees, and taxes.

    Parameters:
        initial_fortune: Starting amount.
        monthly_contribution: Default monthly contribution (used if contributions_schedule is not provided).
        yearly_interest: Annual interest rate (in percent).
        years: Total simulation period in years.
        tax_rate: Tax rate on gains (in percent).
        deposit_at_beginning: Flag indicating whether deposits occur at the beginning of each month.
        transaction_fee: Tuple (fee_value, fee_type) where fee_type is 'ILS' (fixed per year) or 'percentage'
                         (applied on fee-applicable funds).
        management_fee: Tuple (fee_value, fee_type) for management fees; fee_type is either 'percentage'
                        (of balance per month) or 'ILS' (fixed per month).
        initial_already_invested: If True, the initial_fortune is exempt from transaction fees.
        contributions_schedule: Optional 2D array (list of lists) with dimensions [years][12] specifying the
                                contribution amount for each month. If not provided, each month will use monthly_contribution.

    Returns:
        A dictionary containing:
          - 'final_balance': Balance before tax and transaction fees.
          - 'final_balance_taxed': Final balance after applying tax on gains and deducting transaction fees.
          - 'total_deposits': Total amount deposited over the period.
          - 'yearly_balances': List of balances at the end of each year.
          - 'yearly_deposits': List of cumulative deposits at each year-end.
          - 'yearly_earnings': List of earnings (balance minus deposits) at each year-end.
    """
    # If no contributions_schedule is provided, create one using monthly_contribution for every month.
    if contributions_schedule is None:
        contributions_schedule = [[monthly_contribution] * 12 for _ in range(years)]

    def apply_management_fee(balance, percentace_management_fee, ILS_management_fee):
            monthly_rate = percentace_management_fee / 100 / 12
            balance * (1 - monthly_rate)
            return balance - ILS_management_fee

    def apply_interest(balance, forecast_params):
        '''
        see simulate_gbm on forecasting for an explanation of the interest calculation
        '''
        mu = forecast_params['mu']
        sigma = forecast_params['sigma']
        dt = forecast_params['dt']
        z = np.random.standard_normal()  # random draws ~ N(0,1)
        return balance * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)

    def update_monthly_balance(balance, total_deposits, current_contribution, forecast_params):
        balance += current_contribution * (1 - transaction_fee/100)
        balance = apply_management_fee(balance, percentace_management_fee, ILS_management_fee)
        balance = apply_interest(balance, forecast_params)

        total_deposits += current_contribution
        return balance, total_deposits

    # Initial setup
    months = years * 12
    paths = []  # to store the full monthly balance series for each simulation

    # Replace the for-loop over simulation paths with the following vectorized code:

    init_balance = initial_fortune if initial_already_invested else initial_fortune * (1 - transaction_fee / 100)
    balances = np.full(n_sim, init_balance)
    total_deposits = np.full(n_sim, initial_fortune)
    monthly_paths = [balances.copy()]

    mu = forecast_params['mu']
    sigma = forecast_params['sigma']
    dt = forecast_params['dt']

    for m in range(1, months + 1):
        year_idx = (m - 1) // 12
        month_idx = (m - 1) % 12
        current_contribution = contributions_schedule[year_idx][month_idx]

        # Update balances with contributions (transaction fee applied)
        balances += int(current_contribution * (1 - transaction_fee / 100))

        # Apply management fee vectorized
        balances = apply_management_fee(balances, percentace_management_fee, ILS_management_fee)

        # Vectorized interest application
        z = np.random.standard_normal(n_sim)
        balances = balances * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)

        total_deposits += current_contribution
        monthly_paths.append(balances.copy())

    paths = np.array(monthly_paths)
    return paths


def simulate_buying_scenario(apartment_price, down_payment, mortgage_rate, mortgage_term, years,
                             maintenance_cost_rate, fixed_maintenance_cost, yearly_value_increase_rate):
    mortgage_loan = apartment_price - down_payment
    n_payments = mortgage_term * 12
    monthly_rate = mortgage_rate / 12 / 100
    if monthly_rate > 0:
        mortgage_payment = mortgage_loan * (monthly_rate * (1 + monthly_rate) ** n_payments) / (
                    (1 + monthly_rate) ** n_payments - 1)
    else:
        mortgage_payment = mortgage_loan / n_payments

    remaining_balance = mortgage_loan
    total_mortgage_payments = 0
    total_interest_paid = 0
    total_maintenance_cost = 0
    property_value = apartment_price
    total_months = years * 12
    yearly_net_equity = []  # record net equity each year

    # Additional arrays for detailed data
    yearly_mortgage_balance = []
    yearly_principal_paid = []
    yearly_interest_paid = []
    yearly_property_value = []
    yearly_maintenance_cost = []

    # Sums for the current year
    year_principal = 0
    year_interest = 0

    for month in range(1, total_months + 1):
        if month <= n_payments and remaining_balance > 0:
            interest_payment = remaining_balance * monthly_rate
            principal_payment = mortgage_payment - interest_payment
            if principal_payment > remaining_balance:
                principal_payment = remaining_balance
                mortgage_payment = interest_payment + principal_payment
            remaining_balance -= principal_payment
            total_interest_paid += interest_payment
            total_mortgage_payments += mortgage_payment
            year_principal += principal_payment
            year_interest += interest_payment
        if month % 12 == 0:  # end of the year
            annual_maintenance = property_value * (maintenance_cost_rate / 100) + fixed_maintenance_cost
            total_maintenance_cost += annual_maintenance
            property_value *= (1 + yearly_value_increase_rate / 100)
            net_equity = property_value - remaining_balance - total_maintenance_cost
            yearly_net_equity.append(net_equity)
            yearly_mortgage_balance.append(remaining_balance)
            yearly_principal_paid.append(year_principal)
            yearly_interest_paid.append(year_interest)
            yearly_property_value.append(property_value)
            yearly_maintenance_cost.append(total_maintenance_cost)
            # reset yearly sums
            year_principal = 0
            year_interest = 0

    return {
        'final_property_value': property_value,
        'remaining_mortgage': remaining_balance,
        'total_mortgage_payments': total_mortgage_payments,
        'total_interest_paid': total_interest_paid,
        'total_maintenance_cost': total_maintenance_cost,
        'net_equity': net_equity,
        'yearly_net_equity': yearly_net_equity,
        'yearly_mortgage_balance': yearly_mortgage_balance,
        'yearly_principal_paid': yearly_principal_paid,
        'yearly_interest_paid': yearly_interest_paid,
        'yearly_property_value': yearly_property_value,
        'yearly_maintenance_cost': yearly_maintenance_cost
    }


def plot_investment(paths, years, res=12, bins=1000, return_traces=False):
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