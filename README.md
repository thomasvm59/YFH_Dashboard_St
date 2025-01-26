# YHF Dashboard Streamlit Application

## Overview

This project provides an interactive financial dashboard built with **Streamlit**. The dashboard allows users to explore market data, visualize stock performance, and filter data based on specific sectors or symbols. The application uses data from Yahoo Finance, processed using the `yfinance` and `yahooquery` libraries.

### Key Features:
- View all market data in a tree map format.
- Filter the market data by sector or symbol.
- Visualize performance of individual stocks with historical price charts.
- Display financial metrics and other fundamentals for a selected stock.

## Requirements

This project requires Python 3.12 and the following packages:

- **Streamlit** for building the interactive dashboard.
- **Plotly** for interactive plots.
- **Spyder** as the IDE for development.
- **yfinance** and **yahooquery** for fetching financial data.

### Install the required environment:

1. Create a new conda environment:

```bash
conda env list
conda create -n YHF_Dashboard_St python=3.12
conda activate YHF_Dashboard_St

