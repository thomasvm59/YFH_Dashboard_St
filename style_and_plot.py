import plotly.graph_objects as go
import pandas as pd
import streamlit as st 

SHORT_COLUMNS = [
    'price_last', '1d_return', '1w_return', '1m_return', '1y_return',
    'dist_ath', 'price_ath', 'Sector', 'PE Ratio', 'dividendYield',
    'beta', 'marketCap(Bn)', 'volume(mil)', 'shortPercentOfFloat',
    'trailingEps', 'forwardEps', 'shortName'
]

FUNDAMENTALS_COLUMNS = [
    'marketCap(Bn)', 'Revenue(Bn)', 'dividendYield', '5YAvgDiv%',
    'payoutRatio', 'beta', 'trailingPE', 'forwardPE', 'volume(mil)',
    'PE Ratio', 'averageVolume(mil)', 'shortPercentOfFloat',
    'trailingEps', 'forwardEps', 'debtToEquity'
]
  
# Styling Functions
def style_values(value, negative_style="color:red;", positive_style="color:green;"):
    """Apply styles based on value."""
    if pd.isna(value) or isinstance(value, str):
        return None
    return negative_style if value < 0 else positive_style if value > 0 else None


def style_dataframe(summary):
    """Apply styles and formatting to a DataFrame."""
    style_format = {
        '1d_return': '{:.2%}', '1w_return': '{:.2%}', '1m_return': '{:.2%}',
        '1y_return': '{:.2%}', 'dist_ath': '{:.2%}', 'dividendYield': '{:.2%}'
    }
    return summary.style.applymap(style_values).format(style_format, precision=2)

# Data Filtering
def filter_dataframe(summary, default_column="marketCap(Bn)", default_filter_condition=">=", default_value=100):
    """Filter DataFrame based on user inputs."""
    column = st.selectbox("Select column to filter", summary.columns, index=list(summary.columns).index(default_column))
    condition = st.selectbox("Select filter condition", ["=", ">=", "<="], index=["=", ">=", "<="].index(default_filter_condition))
    value = st.number_input("Enter filter value", value=default_value)
    
    filters = {
        "=": lambda df, col, val: df[df[col] == val],
        ">=": lambda df, col, val: df[df[col] >= val],
        "<=": lambda df, col, val: df[df[col] <= val],
    }
    return filters[condition](summary, column, value)

    
# Tree Map Visualization
def create_tree_map(summary):
    """ Filter summary dataframe based on a columns """
    df = summary[['1d_return','marketCap(Bn)','Sector']].reset_index()
    df = df[lambda x : x.Sector!='etf']
    df = df.rename(columns={'index':'id','1d_return' : 'color',
                            'marketCap(Bn)' :'value','Sector':'parent'})
    df_parent = df.copy()
    df_parent['weighted_return']=df_parent['color']*df_parent['value']
    df_parent = df_parent.groupby('parent').sum()[['weighted_return','value']].reset_index()
    df_parent['color']=df_parent['weighted_return']/df_parent['value']
    df_parent = df_parent.rename(columns={'parent':'id'})
    df_parent['parent']='total'
    df_parent = df_parent[['id', 'color', 'value', 'parent']]
    
    all_data = pd.concat([df_parent.dropna(),df])
    colorscale = [[0.0, "red"], [0.5, "white"], [1.0, "green"]]
    
    fig = go.Figure()
    fig.add_trace(go.Treemap(
        labels=all_data['id'],
        parents=all_data['parent'],
        values=all_data['value'],
        branchvalues='total',
        marker=dict(colors=all_data['color'],
                    colorscale=colorscale,            
                    cmin=-0.1,           
                    cmax=0.1            
        ),
        hovertemplate='<b>%{label} </b> <br> MarketCap: %{value:.1f}<br> return: %{color:.2%}',
        name=''
        ))
    
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    return fig

# Multi-Symbol Graph
def plot_multiple_symbols(data, normalize=True):
    """Plot multiple symbols over time."""
    if normalize:
        data = data / data.iloc[0]
    fig = go.Figure()
    for col in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col))
    fig.update_layout(title='Symbol Performance', xaxis_title='Time', yaxis_title='Normalized Prices')
    return fig

# Single Symbol Graph
def plot_single_symbol(data, moving_avgs=(7, 30, 365)):
    """Plot a single symbol with moving averages."""
    symbol = data.columns[0]
    for ma in moving_avgs:
        data[f'price_{ma}_ma'] = data[symbol].rolling(ma).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data[symbol], mode='lines', name=symbol))
    for ma in moving_avgs:
        fig.add_trace(go.Scatter(x=data.index, y=data[f'price_{ma}_ma'], mode='lines', name=f'{ma}d MA'))
    fig.update_layout(title=f'{symbol} Price & Moving Averages', xaxis_title='Time', yaxis_title='Price')
    return fig

                
# Function to display metrics in columns
def display_metrics(columns, metrics, row_data):
    """Display metrics in the specified columns."""
    count = 0
    for metric in metrics:
        with columns[count]:
            st.metric(label=metric, value=row_data[metric])
            count += 1
            if count >= len(columns):
                count = 0

# Function to display price metrics with deltas
def display_price_metrics(columns, price_data, reference_price):
    """Display price metrics and deltas."""
    count = 0
    for price_label, price_value in price_data.items():
        with columns[count]:
            delta = float((reference_price - price_value) / price_value)
            st.metric(label=price_label, value=round(price_value, 1), delta="{:.2%}".format(delta))
            count += 1
            if count >= len(columns):
                count = 0
                
def display_fundamental_metrics(columns, data, pct_columns):
    """Display fundamental metrics in the specified columns."""
    symbol_select = data.index[0]
    count = 0
    for metric in data.columns:
        with columns[count]:
            value = data.loc[symbol_select, metric]
            if metric in pct_columns:
                st.metric(label=metric, value=f"{value * 100:.2f}%")
            else:
                st.metric(label=metric, value=round(value, 1))
            count += 1
            if count >= len(columns):
                count = 0
                
    
    
    
    
    
    
    
    