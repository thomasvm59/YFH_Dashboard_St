"""
Created on Fri Jan 25 2025
@author: TVM
"""

#import relevant libraries (visualization, dashboard, data manipulation)
import pandas as pd 
import streamlit as st
import datetime
from data import get_data
from style_and_plot import (SHORT_COLUMNS, 
                            FUNDAMENTALS_COLUMNS,
                            style_dataframe,
                            filter_dataframe,
                            create_tree_map,
                            plot_multiple_symbols,
                            plot_single_symbol,
                            display_metrics,
                            display_price_metrics,
                            display_fundamental_metrics)

#create dataframes from the function 
now_dt = datetime.datetime.now(tz=datetime.timezone.utc)
now_hr_ts = (now_dt.timestamp() // 3600) * 3600
prices, summary, update_dt = get_data(now_hr_ts)
min_ago = int(max((now_dt - update_dt).total_seconds() // 60, 0))
s = "" if min_ago == 1 else "s"
st.markdown(
    f"""
    Market data was last updated {min_ago} minute{s} ago at
    {str(update_dt)[:16]} UTC."""
) 

###############################################################################
#Start building Streamlit App
###############################################################################

add_sidebar = st.sidebar.selectbox('All Market or Single Stock', ('Market', 'Single Symbol'))

# Title
st.title("Screening App")

#Show individual metrics 
if add_sidebar == 'Market':
    # add table for all available stocks
    st.header("Market Data")
    st.subheader("All Market")
    
    # Plot Map Tree Last Day Return
    fig=create_tree_map(summary)
    st.plotly_chart(fig)
    
    # Plot details dataframes
    df_print=style_dataframe(summary[SHORT_COLUMNS])
    st.dataframe(df_print)
    
    # Plot details dataframes
    st.subheader("Filtered Market")
    filtered_df = filter_dataframe(summary)
    df_print = style_dataframe(filtered_df[SHORT_COLUMNS])
    st.dataframe(df_print)
    
    # add table for specific sector
    st.header("Sector Data")
    sectors = tuple(set(summary['Sector']))
    st.write("Sector Performance")
    sector_select = st.selectbox('Pick a Sector:', sectors, index=list(sectors).index('Technology'))
    df_summary_sector = summary[SHORT_COLUMNS][lambda x : x.Sector==sector_select]
    df_print2 = style_dataframe(df_summary_sector)
    st.dataframe(df_print2)
    
    # Add graph for the Sector
    default_date=datetime.date(2024,1,1)
    symbols_sector = df_summary_sector.index
    graph_start_date_select = st.date_input("Select a starting date for graph:", value=default_date)
    df_graph = prices[symbols_sector].dropna()[lambda x : x.index>=graph_start_date_select.isoformat()]
    fig = plot_multiple_symbols(df_graph)
    st.plotly_chart(fig)
    
if add_sidebar == 'Single Symbol':
    
    st.write("Single Symbol Performance")
    st.subheader("Symbol Performance")
    
    # Select the symbol
    symbol_select = st.selectbox('Pick a Symbol:', 
                                 tuple(summary['symbol']),
                                 index=list(summary['symbol']).index('AAPL'))

    # Display Symbol Fundamentals
    summary_stock = summary.loc[symbol_select].to_frame('fundamentals')
    STR_COLUMNS = ['symbol', 'shortName', 'Sector']
    col1, col2, col3 = st.columns(3)
    display_metrics([col1, col2, col3], STR_COLUMNS, summary_stock['fundamentals'])

    # Display Price Metrics
    summary_stock_price = summary.filter(regex='price').loc[symbol_select].to_frame('prices')
    col1, col2, col3, col4 = st.columns(4)
    display_price_metrics([col1, col2, col3, col4], summary_stock_price['prices'], summary_stock_price.loc['price_last'])

    # Graph Stock Using a slicer 
    all_dates = prices[symbol_select].dropna().index
    min_date = all_dates.min().date()
    max_date = all_dates.max().date()

    graph_start_date_select = st.slider(
        "Select a starting date for the graph:",
        min_value=min_date,
        max_value=max_date,
        value=min_date,
        format="YYYY-MM-DD"
    )
    
    df_graph = prices.loc[lambda x: x.index >= pd.Timestamp(graph_start_date_select)][[symbol_select]]
    fig = plot_single_symbol(df_graph)
    st.plotly_chart(fig)
    
    st.subheader("Symbol Fundamentals")

    summary_stock = summary[FUNDAMENTALS_COLUMNS].loc[[symbol_select]].dropna(axis=1)
    pct_columns = ['dividendYield', 'shortPercentOfFloat']

    col1, col2, col3, col4, col5 = st.columns(5)
    display_fundamental_metrics([col1, col2, col3, col4, col5], summary_stock, pct_columns)
                
        
