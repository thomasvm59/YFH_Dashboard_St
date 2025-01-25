"""
Created on Wed Jan 25

@author: Thomas Van Moerkercke
"""

#import relevant libraries (visualization, dashboard, data manipulation)
import pandas as pd 
import plotly.graph_objects as go
import streamlit as st
import datetime
from data import get_data

#Define Functions 
def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try: 
        return props if v < 0 else None
    except:
        pass
    
def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try: 
        return props if v > 0 else None
    except:
        pass  

#create dataframes from the function 
prices, summary = get_data()

SHORT_COLUMNS = ['last_price', 
                 '1d_return','1w_return','1m_return','1y_return', 'dist_ath',
                 'ATH Price', 'Sector', 'PE Ratio', 'dividendYield', 'beta', 'marketCap(Bn)', 'volume(mil)',
                 'shortPercentOfFloat', 'trailingEps', 'forwardEps', 'shortName']

###############################################################################
#Start building Streamlit App
###############################################################################

add_sidebar = st.sidebar.selectbox('All Market or Single Stock', ('Market', 'Single Symbol'))

# Title
st.title("Screening App")

#Show individual metrics 
if add_sidebar == 'Market':
    # add table for all available stocks
    st.write("Market Data")

    df_summary_final = summary[SHORT_COLUMNS]
    df_print = df_summary_final.style.hide(
    ).applymap(style_negative, props='color:red;'
    ).applymap(style_positive, props='color:green;'
    ).format(
    {
        '1d_return': '{:.2%}', 
        '1w_return': '{:.2%}', 
        '1m_return': '{:.2%}', 
        '1y_return': '{:.2%}', 
        'dist_ath': '{:.2%}', 
        'dividendYield': '{:.2%}'
    }, 
    precision=2)
    st.dataframe(df_print)
    
    # add table for specific sector
    
    sectors = tuple(summary['Sector'])
    st.write("Sector Performance")
    sector_select = st.selectbox('Pick a Sector:', sectors)
    
    df_summary_final2 = summary[SHORT_COLUMNS][lambda x : x.Sector==sector_select]
    df_print2 = df_summary_final2.style.hide(
    ).applymap(style_negative, props='color:red;'
    ).applymap(style_positive, props='color:green;'
    ).format(
    {
        '1d_return': '{:.2%}', 
        '1w_return': '{:.2%}', 
        '1m_return': '{:.2%}', 
        '1y_return': '{:.2%}', 
        'dist_ath': '{:.2%}', 
        'dividendYield': '{:.2%}'
    }, 
    precision=2)
    st.dataframe(df_print2)
        
    default_date=datetime.date(2024,1,1)
    symbols_sector = df_summary_final2.index
    graph_start_date_select = st.date_input("Select a starting date for graph:", value=default_date)
    df_graph = prices[symbols_sector].dropna()[lambda x : x.index>=graph_start_date_select.isoformat()]
    normalize=True
    if normalize:
        df_graph=df_graph/df_graph.iloc[0]
        
    fig = go.Figure()
    for symbol in symbols_sector:
        fig.add_trace(go.Scatter(x=df_graph.index, y=df_graph[symbol], 
                                 mode='lines',
                                 name=symbol))

    fig.update_layout(title='',
                   xaxis_title='Time',
                   yaxis_title='prices')
    
    st.plotly_chart(fig)

    
if add_sidebar == 'Single Symbol':
    
    st.write("Single Symbol Performance")
    symbols = tuple(summary['symbol'])
    symbol_select = st.selectbox('Pick a Symbol:', symbols)
    
    # Define date range for slider
    all_dates = prices[symbol_select].index
    min_date = all_dates.min().date()
    max_date = all_dates.max().date()
    
    # Use slider to select starting date
    graph_start_date_select = st.slider(
        "Select a starting date for the graph:",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        format="YYYY-MM-DD"
    )
    
    # Filter data based on selected date
    df_graph = prices[symbol_select].loc[lambda x: x.index >= pd.Timestamp(graph_start_date_select)].to_frame('price')
    df_graph['price_7_ma']=df_graph['price'].rolling(7).mean()
    df_graph['price_30_ma']=df_graph['price'].rolling(30).mean()
    df_graph['price_365_ma']=df_graph['price'].rolling(365).mean()
    
    # Plot the graph
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_graph.index, y=df_graph['price'], 
                              mode='lines',
                              name=symbol_select))
    fig2.add_trace(go.Scatter(x=df_graph.index, y=df_graph['price_30_ma'],
                        mode='lines',
                        name='30d_ma', line=dict(color='orange', dash ='dash')))
    fig2.add_trace(go.Scatter(x=df_graph.index, y=df_graph['price_7_ma'],
                        mode='lines',
                        name='7d_ma', line=dict(color='black', dash ='dash')))
    fig2.add_trace(go.Scatter(x=df_graph.index, y=df_graph['price_365_ma'],
                        mode='lines', 
                        name='365d_ma', line=dict(color='pink', dash ='dash')))
    
    fig2.update_layout(
        title=f'Price of {symbol_select}',
        xaxis_title='Time',
        yaxis_title='Prices'
    )
    
    st.plotly_chart(fig2)
        




