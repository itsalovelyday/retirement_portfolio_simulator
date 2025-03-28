import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.io as pio

# Initialize the Dash app
app = dash.Dash(__name__)

# Define parameters
def get_default_params():
    return {
        'starting_age': 24,
        'retirement_age': 65,
        'monthly_income': 5000,
        'monthly_expenses': 3500,
        'annual_return_rate': 0.07,
        'annual_volatility': 0.15,
        'inflation_rate': 0.03,
        'initial_investment': 50000,
        'num_simulations': 100
    }

# Function to calculate trailing returns
def calculate_trailing_return(returns, window=24):
    trailing_returns = []
    for i in range(len(returns)):
        if i < window:
            trailing_returns.append(np.nan)
        else:
            # Calculate the total return over the window period
            window_returns = returns[i-window:i]
            # Calculate cumulative return using compound interest formula
            cumulative_return = np.prod(1 + window_returns) - 1
            # Annualize the return
            annualized_return = (1 + cumulative_return)**(12/window) - 1
            trailing_returns.append(annualized_return)
    return trailing_returns

# Function to generate simulation data
def generate_simulation(params):
    starting_date = pd.to_datetime('2025-01-01')
    # Calculate months until retirement
    num_months = (params['retirement_age'] - params['starting_age']) * 12
    date_range = pd.date_range(start=starting_date, periods=num_months, freq='ME')
    
    # Initialize DataFrame
    df = pd.DataFrame(index=date_range)
    
    # Add columns
    df['Age'] = params['starting_age'] + (df.index - df.index[0]).days / 365.25
    
    # Calculate monthly income and expenses with inflation
    df['Monthly_Income'] = params['monthly_income'] * (1 + params['inflation_rate'])**(df['Age'] - params['starting_age'])
    df['Monthly_Expenses'] = params['monthly_expenses'] * (1 + params['inflation_rate'])**(df['Age'] - params['starting_age'])
    df['Monthly_Investment'] = df['Monthly_Income'] - df['Monthly_Expenses']
    
    # Generate returns
    monthly_volatility = params['annual_volatility'] / np.sqrt(12)
    monthly_expected_return = (1 + params['annual_return_rate'])**(1/12) - 1
    
    monthly_returns = np.random.normal(
        loc=monthly_expected_return,
        scale=monthly_volatility,
        size=len(df)
    )
    
    # Calculate portfolio value
    df['Portfolio_Value'] = 0.0
    current_portfolio = params['initial_investment']
    flat_interest_rate = 0.05  # 5% flat interest rate for negative portfolio values
    
    for i in range(len(df)):
        if i == 0:
            # First month calculation
            portfolio_with_investment = current_portfolio + df.iloc[i, df.columns.get_loc('Monthly_Investment')]
            if portfolio_with_investment >= 0:
                df.iloc[i, df.columns.get_loc('Portfolio_Value')] = portfolio_with_investment * (1 + monthly_returns[i])
            else:
                df.iloc[i, df.columns.get_loc('Portfolio_Value')] = portfolio_with_investment * (1 + flat_interest_rate/12)
            current_portfolio = df.iloc[i, df.columns.get_loc('Portfolio_Value')]
        else:
            # Subsequent months
            portfolio_with_investment = current_portfolio + df.iloc[i, df.columns.get_loc('Monthly_Investment')]
            if portfolio_with_investment >= 0:
                current_portfolio = portfolio_with_investment * (1 + monthly_returns[i])
            else:
                current_portfolio = portfolio_with_investment * (1 + flat_interest_rate/12)
            df.iloc[i, df.columns.get_loc('Portfolio_Value')] = current_portfolio
    
    # Calculate trailing returns
    trailing_returns = calculate_trailing_return(monthly_returns)
    return df, trailing_returns

# App layout
app.layout = html.Div([
    html.H1('Retirement Portfolio Simulator', 
            style={'textAlign': 'center', 
                   'color': '#2c3e50',
                   'marginBottom': '30px',
                   'fontFamily': 'Arial, sans-serif'}),
    
    # Main content area with flex layout
    html.Div([
        # Parameters section - now in a sidebar
        html.Div([
            html.H3('Parameters', 
                    style={'color': '#2c3e50', 
                           'marginBottom': '20px',
                           'fontFamily': 'Arial, sans-serif'}),
            html.Div([
                html.Div([
                    html.Label('Starting Age', style={'fontWeight': 'bold'}),
                    dcc.Input(id='starting-age', type='number', value=24, 
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Retirement Age', style={'fontWeight': 'bold'}),
                    dcc.Input(id='retirement-age', type='number', value=65,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Starting Portfolio', style={'fontWeight': 'bold'}),
                    dcc.Input(id='initial-investment', type='number', value=50000,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Monthly Income', style={'fontWeight': 'bold'}),
                    dcc.Input(id='monthly-income', type='number', value=5000,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Monthly Expenses', style={'fontWeight': 'bold'}),
                    dcc.Input(id='monthly-expenses', type='number', value=3500,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Expected Annual Return (%)', style={'fontWeight': 'bold'}),
                    dcc.Input(id='annual-return', type='number', value=7, step=0.1,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Annual Volatility (%)', style={'fontWeight': 'bold'}),
                    dcc.Input(id='annual-volatility', type='number', value=15, step=0.1,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Inflation Rate (%)', style={'fontWeight': 'bold'}),
                    dcc.Input(id='inflation-rate', type='number', value=3, step=0.1,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Div([
                    html.Label('Number of Simulations', style={'fontWeight': 'bold'}),
                    dcc.Input(id='num-simulations', type='number', value=100,
                             min=10, max=1000, step=10,
                             style={'width': '100%', 'marginBottom': '15px'})
                ]),
                html.Button('Run Simulation', 
                           id='run-simulation', 
                           n_clicks=0,
                           style={'width': '100%',
                                  'padding': '10px',
                                  'backgroundColor': '#3498db',
                                  'color': 'white',
                                  'border': 'none',
                                  'borderRadius': '5px',
                                  'cursor': 'pointer',
                                  'fontSize': '16px',
                                  'marginTop': '10px'})
            ], style={'padding': '20px'})
        ], style={'width': '300px',
                  'backgroundColor': '#f8f9fa',
                  'borderRadius': '10px',
                  'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                  'marginRight': '20px'}),
        
        # Main content area with graph and statistics
        html.Div([
            # Graph
            dcc.Graph(id='simulation-graph',
                     style={'height': '600px',
                            'backgroundColor': 'white',
                            'borderRadius': '10px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                            'marginBottom': '20px'}),
            
            # Statistics
            html.Div(id='statistics',
                     style={'backgroundColor': '#f8f9fa',
                            'padding': '20px',
                            'borderRadius': '10px',
                            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ], style={'flex': '1'})
    ], style={'display': 'flex',
               'padding': '20px',
               'gap': '20px'})
], style={'backgroundColor': '#f0f2f5',
           'minHeight': '100vh'})

@app.callback(
    [Output('simulation-graph', 'figure'),
     Output('statistics', 'children')],
    [Input('run-simulation', 'n_clicks')],
    [State('starting-age', 'value'),
     State('retirement-age', 'value'),
     State('monthly-income', 'value'),
     State('monthly-expenses', 'value'),
     State('annual-return', 'value'),
     State('annual-volatility', 'value'),
     State('inflation-rate', 'value'),
     State('initial-investment', 'value'),
     State('num-simulations', 'value')]
)
def update_graph(n_clicks, starting_age, retirement_age, monthly_income, 
                monthly_expenses, annual_return, annual_volatility, inflation_rate,
                initial_investment, num_simulations):
    if n_clicks == 0:
        return {}, "Click 'Run Simulation' to start"
    
    # Convert percentage inputs to decimals
    annual_return = annual_return / 100
    annual_volatility = annual_volatility / 100
    inflation_rate = inflation_rate / 100
    
    # Generate parameters
    params = {
        'starting_age': starting_age,
        'retirement_age': retirement_age,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'annual_return_rate': annual_return,
        'annual_volatility': annual_volatility,
        'inflation_rate': inflation_rate,
        'initial_investment': initial_investment,
        'num_simulations': num_simulations
    }
    
    # Generate simulations
    all_simulations = []
    all_trailing_returns = []
    
    for _ in range(params['num_simulations']):
        df, trailing_returns = generate_simulation(params)
        all_simulations.append(df)
        all_trailing_returns.append(trailing_returns)
    
    # Create figure
    fig = go.Figure()
    
    # Add traces for each simulation
    for i in range(params['num_simulations']):
        fig.add_trace(go.Scatter(
            x=all_simulations[i].index,
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
            hoverlabel=dict(
                bgcolor='white',
                font=dict(size=12)
            ),
            hovertemplate='%{text}<extra></extra>',
            hoveron='points+fills'
        ))
    
    # Calculate statistics
    final_values = [sim['Portfolio_Value'].iloc[-1] for sim in all_simulations]
    avg_final = np.mean(final_values)
    median_final = np.median(final_values)
    p10_final = np.percentile(final_values, 10)
    p90_final = np.percentile(final_values, 90)
    
    # Calculate expected monthly investment income using 4% safe withdrawal rate
    safe_withdrawal_rate = 0.04
    monthly_rate = safe_withdrawal_rate / 12
    
    stats = html.Div([
        html.H3('Simulation Statistics', 
                style={'color': '#2c3e50',
                       'marginBottom': '15px',
                       'fontFamily': 'Arial, sans-serif'}),
        html.Div([
            html.Div([
                html.P('Average Final Portfolio Value:', 
                       style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.P(f'${avg_final:,.0f}',
                       style={'fontSize': '18px', 'color': '#2c3e50'}),
                html.P(f'Monthly Income: ${avg_final * monthly_rate:,.0f}',
                       style={'fontSize': '14px', 'color': '#7f8c8d'})
            ], style={'flex': '1', 'textAlign': 'center'}),
            html.Div([
                html.P('Median Final Portfolio Value:', 
                       style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.P(f'${median_final:,.0f}',
                       style={'fontSize': '18px', 'color': '#2c3e50'}),
                html.P(f'Monthly Income: ${median_final * monthly_rate:,.0f}',
                       style={'fontSize': '14px', 'color': '#7f8c8d'})
            ], style={'flex': '1', 'textAlign': 'center'}),
            html.Div([
                html.P('10th Percentile:', 
                       style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.P(f'${p10_final:,.0f}',
                       style={'fontSize': '18px', 'color': '#2c3e50'}),
                html.P(f'Monthly Income: ${p10_final * monthly_rate:,.0f}',
                       style={'fontSize': '14px', 'color': '#7f8c8d'})
            ], style={'flex': '1', 'textAlign': 'center'}),
            html.Div([
                html.P('90th Percentile:', 
                       style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                html.P(f'${p90_final:,.0f}',
                       style={'fontSize': '18px', 'color': '#2c3e50'}),
                html.P(f'Monthly Income: ${p90_final * monthly_rate:,.0f}',
                       style={'fontSize': '14px', 'color': '#7f8c8d'})
            ], style={'flex': '1', 'textAlign': 'center'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ])
    
    # Update layout
    fig.update_layout(
        title='Retirement Portfolio Growth Simulations',
        xaxis_title='Year',
        yaxis_title='Portfolio Value (USD)',
        hovermode='closest',
        showlegend=False,
        template='plotly_white',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        shapes=[
            # Add vertical line at retirement age
            dict(
                type="line",
                x0=all_simulations[-1].index[-1],
                x1=all_simulations[-1].index[-1],
                y0=0,
                y1=max(sim['Portfolio_Value'].max() for sim in all_simulations),
                line=dict(
                    color="red",
                    width=1,
                    dash="dash"
                ),
                name="Retirement Age"
            )
        ]
    )
    
    return fig, stats

if __name__ == '__main__':
    try:
        app.run(debug=True, port=8050)
    except Exception as e:
        print(f"Error starting the server: {e}")
        print("Make sure you have all required dependencies installed:")
        print("pip install dash plotly pandas numpy") 