import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio

# Set the default renderer to 'browser'
pio.renderers.default = 'browser'

# Define parameters
starting_age = 24
retirement_age = 65
starting_date = pd.to_datetime('2025-01-01')
monthly_income = 5000
monthly_expenses = 3500
monthly_investment = monthly_income - monthly_expenses
annual_return_rate = 0.07  # 7% expected annual return
annual_volatility = 0.15   # 15% annual volatility (standard deviation)
monthly_volatility = annual_volatility / np.sqrt(12)  # Convert annual to monthly volatility
monthly_expected_return = (1 + annual_return_rate)**(1/12) - 1
inflation_rate = 0.03  # 3% annual inflation

# Add market crash simulation parameters
crash_probability = 0.02  # 2% chance of a market crash each month
crash_return = -0.20     # 20% drop during a crash
crash_recovery_months = 12  # Months to recover from a crash

# Calculate number of months until retirement
num_months = (retirement_age - starting_age) * 12

# Create date range for index
date_range = pd.date_range(start=starting_date, periods=num_months, freq='ME')

# Function to calculate trailing 36-month return
def calculate_trailing_return(returns, window=36):
    trailing_returns = []
    for i in range(len(returns)):
        if i < window:
            trailing_returns.append(np.nan)
        else:
            # Calculate annualized return over the trailing window
            window_returns = returns[i-window:i]
            annualized_return = (1 + np.prod(1 + window_returns))**(12/window) - 1
            trailing_returns.append(annualized_return)
    return trailing_returns

# Generate multiple simulations
num_simulations = 100
all_simulations = []
all_trailing_returns = []

for sim in range(num_simulations):
    # Initialize DataFrame for this simulation
    df = pd.DataFrame(index=date_range)
    
    # Add columns
    df['Age'] = starting_age + (df.index - df.index[0]).days / 365.25
    df['Monthly_Income'] = monthly_income * (1 + inflation_rate)**(df['Age'] - starting_age)
    df['Monthly_Expenses'] = monthly_expenses * (1 + inflation_rate)**(df['Age'] - starting_age)
    df['Monthly_Investment'] = df['Monthly_Income'] - df['Monthly_Expenses']
    
    # Generate random monthly returns with market crashes
    monthly_returns = np.random.normal(
        loc=monthly_expected_return,
        scale=monthly_volatility,
        size=len(df)
    )
    
    # Simulate market crashes
    crash_months = np.random.random(len(df)) < crash_probability
    for i in range(len(df)):
        if crash_months[i]:
            # Apply crash return
            monthly_returns[i] = crash_return
            # Add recovery period
            recovery_months = min(crash_recovery_months, len(df) - i)
            for j in range(1, recovery_months):
                if i + j < len(df):
                    # Gradual recovery with increased volatility
                    monthly_returns[i + j] = np.random.normal(
                        loc=monthly_expected_return * (j / recovery_months),
                        scale=monthly_volatility * 1.5,
                        size=1
                    )[0]
    
    # Calculate portfolio value
    df['Portfolio_Value'] = 0.0
    current_portfolio = 50000  # Initial investment
    
    for i in range(len(df)):
        if i == 0:
            df.iloc[i, df.columns.get_loc('Portfolio_Value')] = (current_portfolio + 
                df.iloc[i, df.columns.get_loc('Monthly_Investment')]) * (1 + monthly_returns[i])
            current_portfolio = df.iloc[i, df.columns.get_loc('Portfolio_Value')]
        else:
            current_portfolio = (current_portfolio * (1 + monthly_returns[i]) + 
                               df.iloc[i, df.columns.get_loc('Monthly_Investment')])
            df.iloc[i, df.columns.get_loc('Portfolio_Value')] = current_portfolio
    
    # Calculate trailing returns with more realistic window
    trailing_returns = calculate_trailing_return(monthly_returns, window=24)  # Changed to 24 months
    
    all_simulations.append(df)
    all_trailing_returns.append(trailing_returns)

# Create interactive plot
fig = go.Figure()

# Add traces for each simulation
for i in range(num_simulations):
    fig.add_trace(go.Scatter(
        x=date_range,
        y=all_simulations[i]['Portfolio_Value'],
        mode='lines',
        line=dict(
            color='rgba(128, 128, 128, 0.1)',
            width=1
        ),
        hoverinfo='text',
        text=[f"Age: {age:.1f}<br>"
              f"Portfolio Value: ${value:,.0f}<br>"
              f"Monthly Income: ${income:,.0f}<br>"
              f"2-Year Return: {ret:.1%}"
              for age, value, income, ret in zip(
                  all_simulations[i]['Age'],
                  all_simulations[i]['Portfolio_Value'],
                  all_simulations[i]['Monthly_Income'],
                  all_trailing_returns[i]
              )],
        showlegend=False,
        name=f'Simulation {i+1}',
        hoverlabel=dict(bgcolor='white'),
        hovertemplate='%{text}<extra></extra>',
        hoveron='points+fills',
        hoverdistance=100
    ))

# Update layout with hover effects
fig.update_layout(
    title='Retirement Portfolio Growth Simulations',
    xaxis_title='Year',
    yaxis_title='Portfolio Value (USD)',
    hovermode='closest',
    showlegend=False,
    template='plotly_white',
    hoverdistance=100,
    spikedistance=1000
)

# Add hover effect to change line color dynamically
fig.update_traces(
    selector=dict(mode='lines'),
    line=dict(
        color='rgba(128, 128, 128, 0.1)',
        width=1
    ),
    hoverlabel=dict(
        bgcolor='white',
        font=dict(size=12)
    )
)

# Add hover effect to highlight lines
fig.update_traces(
    hoveron='points+fills',
    hoverinfo='text',
    line=dict(
        color='rgba(128, 128, 128, 0.1)',
        width=1
    ),
    hoverlabel=dict(
        bgcolor='white',
        font=dict(size=12)
    )
)

# Update the parameter box text to be more concise
param_text = (f'Parameters:<br>'
             f'Age: {starting_age} → {retirement_age}<br>'
             f'Income: ${monthly_income:,.0f}/mo<br>'
             f'Expenses: ${monthly_expenses:,.0f}/mo<br>'
             f'Expected Return: {annual_return_rate:.1%}/yr<br>'
             f'Inflation: {inflation_rate:.1%}/yr')

fig.add_annotation(
    text=param_text,
    xref='paper',
    yref='paper',
    x=0.95,
    y=0.05,
    showarrow=False,
    align='right',
    bgcolor='rgba(255, 255, 255, 0.8)',
    bordercolor='gray',
    borderwidth=1,
    borderpad=4,
    font=dict(size=12)
)

# Show the plot
fig.show()
# Also save the plot as HTML for backup
fig.write_html("retirement_simulation.html")