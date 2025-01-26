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
now_dt = datetime.datetime.now(tz=datetime.timezone.utc)
now_hr_ts = (now_dt.timestamp() // 3600) * 3600
prices_equity, prices_crypto, summary_equity, summary_cryto, update_dt = get_data(now_hr_ts)
min_ago = int(max((now_dt - update_dt).total_seconds() // 60, 0))
s = "" if min_ago == 1 else "s"
st.markdown(
    f"""
    Market data was last updated {min_ago} minute{s} ago at
    {str(update_dt)[:16]} UTC."""
)

SHORT_COLUMNS = ['price_last', 
                 '1d_return','1w_return','1m_return','1y_return', 'dist_ath',
                 'price_ath', 'Sector', 'PE Ratio', 'dividendYield', 'beta', 'marketCap(Bn)', 'volume(mil)',
                 'shortPercentOfFloat', 'trailingEps', 'forwardEps', 'shortName']

FUNDAMENTALS=[
        'marketCap(Bn)', 'Revenue(Bn)',
        'dividendYield', 'fiveYearAvgDividendYield', 'payoutRatio', 
        'beta', 'trailingPE', 'forwardPE', 'volume(mil)', 'PE Ratio', 
        'averageVolume(mil)', 'shortPercentOfFloat', 'trailingEps', 
        'forwardEps','debtToEquity']   

###############################################################################
#Start building Streamlit App
###############################################################################

add_sidebar = st.sidebar.selectbox('All Market or Single Stock', ('Market', 'Single Symbol'))

# Title
st.title("Screening App")

summary = pd.concat([summary_equity,summary_cryto])
prices = pd.concat([prices_equity,prices_crypto],axis=1).ffill()

#Show individual metrics 
if add_sidebar == 'Market':
    # add table for all available stocks
    st.header("Market Data")
    st.subheader("All Market")
    
    heat_map = summary[['1d_return','marketCap(Bn)','Sector']].reset_index()
    heat_map = heat_map[lambda x : x.Sector!='etf']
    heat_map  = heat_map.rename(columns={'index':'id',
                                        '1d_return' : 'color',
                                        'marketCap(Bn)' :'value',
                                        'Sector':'parent'})
    df_parent = heat_map.copy()
    df_parent['weighted_return']=df_parent['color']*df_parent['value']
    df_parent = df_parent.groupby('parent').sum()[['weighted_return','value']].reset_index()
    df_parent['color']=df_parent['weighted_return']/df_parent['value']
    df_parent = df_parent.rename(columns={'parent':'id'})
    df_parent['parent']='total'
    df_parent = df_parent[['id', 'color', 'value', 'parent']]
    df_concat = pd.concat([df_parent.dropna(),heat_map])
    df_all_trees = df_concat.copy()
    # Define the custom diverging colorscale
    color_ = [[0.0, "red"],   # Max red for -0.1
              [0.5, "white"], # Neutral for 0
              [1.0, "green"]] # Max green for 0.1
    
    # Define the range for colors
    max_positive = 0.1
    max_negative = -0.1
    average_score=0
    
    fig = go.Figure()
    
    fig.add_trace(go.Treemap(
        labels=df_all_trees['id'],
        parents=df_all_trees['parent'],
        values=df_all_trees['value'],
        branchvalues='total',
        marker=dict(
            colors=df_all_trees['color'],  
            colorscale=color_,            
            cmin=max_negative,           
            cmax=max_positive            
        ),
        hovertemplate='<b>%{label} </b> <br> MarketCap: %{value:.1f}<br> return: %{color:.2%}',
        name=''
        ))
    
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig)
    
    df_summary_final = summary[SHORT_COLUMNS]
    df_print = df_summary_final.style.hide(
    ).map(style_negative, props='color:red;'
    ).map(style_positive, props='color:green;'
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
    
    st.subheader("Filtered Market")
    
    default_column = "marketCap(Bn)"  
    default_filter_condition = ">="

    # User selects the column to filter
    column = st.selectbox(
        "Select column to filter", 
        summary.columns, 
        index=list(summary.columns).index(default_column)
    )
    filter_condition = st.selectbox(
        "Select filter condition",
        ["=", ">=", "<="],
        index=["=", ">=", "<="].index(default_filter_condition)
    )
    # User inputs the filter value
    filter_value = st.number_input("Enter filter value", value=100)
    # Apply the filter
    if filter_condition == "=":
        filtered_df = summary[summary[column] == filter_value][SHORT_COLUMNS]
    elif filter_condition == ">=":
        filtered_df = summary[summary[column] >= filter_value][SHORT_COLUMNS]
    elif filter_condition == "<=":
        filtered_df = summary[summary[column] <= filter_value][SHORT_COLUMNS]
    df_print = filtered_df.style.hide(
    ).map(style_negative, props='color:red;'
    ).map(style_positive, props='color:green;'
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
    
    st.header("Sector Data")
    

    sectors = tuple(set(summary['Sector']))
    st.write("Sector Performance")
    sector_select = st.selectbox('Pick a Sector:', sectors)
    
    df_summary_final2 = summary[SHORT_COLUMNS][lambda x : x.Sector==sector_select]
    df_print2 = df_summary_final2.style.hide(
    ).map(style_negative, props='color:red;'
    ).map(style_positive, props='color:green;'
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
    st.subheader("Symbol Performance")
    symbols = tuple(summary['symbol'])
    symbol_select = st.selectbox('Pick a Symbol:', 
                                 tuple(summary['symbol']),
                                 index=list(summary['symbol']).index('AAPL'),
                                 )

    summary_stock=summary.loc[symbol_select].to_frame('fundamentals')
    STR_COLUMNS=['symbol', 'shortName', 'Sector']
    col1, col2, col3= st.columns(3)
    columns = [col1, col2, col3]
    count = 0
    for i in STR_COLUMNS:
        with columns[count]:
            st.metric(label= i, value = summary_stock.loc[i]['fundamentals'])
            count += 1    
    
    summary_stock_price = summary.filter(regex='price').loc[symbol_select].to_frame('prices')    
    col1, col2, col3, col4 = st.columns(4)
    columns = [col1, col2, col3, col4]
    count = 0
    for i in summary_stock_price.index:
        with columns[count]:
            delta = float((summary_stock_price.loc['price_last'] - summary_stock_price.loc[i])/summary_stock_price.loc[i])
            st.metric(label= i, value = round(summary_stock_price.loc[i],1), delta = "{:.2%}".format(delta))
            count += 1
            if count >= 4:
                count = 0
                
    # Define date range for slider
    all_dates = prices[symbol_select].dropna().index
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
    
    st.subheader("Symbol Fundamentals")

    summary_stock=summary[FUNDAMENTALS].loc[symbol_select].to_frame('fundamentals').dropna()
    pct_columns = ['dividendYield','shortPercentOfFloat']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    count = 0
    for i in summary_stock.index:
        with columns[count]:
            if i in pct_columns:
                value = summary_stock.loc[i]['fundamentals']
                st.metric(label= i, value = f"{value * 100:.2f}%")
            else:
                st.metric(label= i, value = round(summary_stock.loc[i]['fundamentals'],1))
            count += 1
            if count >= 5:
                count = 0
                
        
