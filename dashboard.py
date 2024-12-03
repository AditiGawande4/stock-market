import streamlit as st
import pandas as pd
import boto3
import time
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Market Analysis", layout="wide")

# AWS Athena Configurations
AWS_REGION = "us-east-2" # Replace with your AWS region
S3_OUTPUT = "s3://stock-market-query-target/"  # Replace with your S3 bucket
DATABASE = "stock_market_kafka"  # Replace with your Athena database

# Athena Query Function
def query_athena(query):
    client = boto3.client('athena', region_name=AWS_REGION)
    try:
        response = client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': DATABASE},
            ResultConfiguration={'OutputLocation': S3_OUTPUT}
        )
        query_execution_id = response['QueryExecutionId']

        # Wait for query to complete
        while True:
            status = client.get_query_execution(QueryExecutionId=query_execution_id)["QueryExecution"]["Status"]["State"]
            if status in ["SUCCEEDED", "FAILED"]:
                break
            time.sleep(1)

        if status == "FAILED":
            reason = client.get_query_execution(QueryExecutionId=query_execution_id)["QueryExecution"]["Status"]["StateChangeReason"]
            raise Exception(f"Athena query failed: {reason}")

        # Fetch query results
        results = client.get_query_results(QueryExecutionId=query_execution_id)

        # Extract column labels
        if "Rows" not in results["ResultSet"] or len(results["ResultSet"]["Rows"]) == 0:
            return pd.DataFrame()  # Return empty DataFrame if no rows found

        columns = [col["Label"] for col in results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]]

        # Extract data rows
        rows = [
            [datum.get("VarCharValue", None) for datum in row["Data"]]
            for row in results["ResultSet"]["Rows"][1:]  # Skip column headers
        ]

        return pd.DataFrame(rows, columns=columns)

    except Exception as e:
        st.error(f"Error querying Athena: {e}")
        return pd.DataFrame()

# Query Athena
QUERY = """
SELECT * FROM "stock-market-kafka"."kafka_stock_market_project_aditi";
"""
data = query_athena(QUERY)

if not data.empty:
    # Data Preparation
    data['date'] = pd.to_datetime(data['date'], errors='coerce')  # Fix date conversion issues
    data['open'] = pd.to_numeric(data['open'], errors='coerce')
    data['high'] = pd.to_numeric(data['high'], errors='coerce')
    data['low'] = pd.to_numeric(data['low'], errors='coerce')
    data['close'] = pd.to_numeric(data['close'], errors='coerce')
    data['volume'] = pd.to_numeric(data['volume'], errors='coerce')
    data['closeusd'] = pd.to_numeric(data['closeusd'], errors='coerce')

    # Drop rows with NaN values in critical columns
    data = data.dropna(subset=['date', 'open', 'high', 'low', 'close', 'volume'])

    # Prepare indices for selection
    data['index'] = data['index'].str.strip().str.upper()
    unique_indices = sorted(data['index'].unique())
    selected_index = st.selectbox("Select Index for Visualization:", unique_indices)

    # Filter Data by Selected Index
    filtered_data = data[data['index'] == selected_index].copy()

    # Ensure dates are ordered for each index
    filtered_data = filtered_data.sort_values(by='date')

    # 1. Candlestick Chart
    st.write(f"### Candlestick Chart for {selected_index}")

    # Dynamically calculate the Y-axis range
    y_min = filtered_data['low'].min() - 50  # Add some padding below the minimum value
    y_max = filtered_data['high'].max() + 50  # Add some padding above the maximum value

    # Adjust the x-axis range to zoom in, showing fewer candlesticks for larger size
    x_min = filtered_data['date'].min()
    x_max = filtered_data['date'].max()

    fig_candle = go.Figure(data=[go.Candlestick(
        x=filtered_data['date'],
        open=filtered_data['open'],
        high=filtered_data['high'],
        low=filtered_data['low'],
        close=filtered_data['close'],
        increasing_line_width=3,  # Set larger width for increasing candlesticks
        decreasing_line_width=3,  # Set larger width for decreasing candlesticks
    )])
    fig_candle.update_layout(
        title=f'Candlestick Chart: {selected_index}',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis=dict(
            range=[x_min, x_max],  # Adjust the range to control zoom level
        ),
        yaxis=dict(
            tick0=y_min,  # Start tick at the dynamically calculated minimum
            dtick=(y_max - y_min) / 10,  # Dynamic tick interval
            range=[y_min, y_max],  # Dynamically set Y-axis range
        ),
        hovermode="x unified",  # Ensure consistent tooltips
        template='plotly_dark',
        width=1100,  # Increased width
        height=700,  # Increased height
    )
    st.plotly_chart(fig_candle, use_container_width=False)

    # 2. Moving Average Chart
    st.write(f"### Moving Average of Close Prices for {selected_index}")
    filtered_data['MA_10'] = filtered_data['close'].rolling(window=10).mean()
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(x=filtered_data['date'], y=filtered_data['close'], mode='lines', name='Close Price'))
    fig_ma.add_trace(go.Scatter(x=filtered_data['date'], y=filtered_data['MA_10'], mode='lines', name='10-Day MA'))
    fig_ma.update_layout(
        title=f'Moving Average: {selected_index}',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark'
    )
    st.plotly_chart(fig_ma, use_container_width=True)

    # 4. Correlation Heatmap
    st.write(f"### Correlation Heatmap for {selected_index}")
    correlation_data = filtered_data[['open', 'high', 'low', 'close', 'volume']].corr()

    # Adjust the figure size and make text horizontal
    fig, ax = plt.subplots(figsize=(3, 3))  # Smaller size
    sns.heatmap(correlation_data, annot=True, cmap="coolwarm", ax=ax, cbar_kws={'shrink': 0.5})  # Adjust color bar
    ax.set_title(f"Correlation Heatmap: {selected_index}", fontsize=10)  # Smaller title font
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=8)  # Horizontal x-axis labels
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)  # Horizontal y-axis labels

    # Reduce the space taken on the webpage by placing it in a single narrow column
    col1, col2, col3 = st.columns([1, 2, 1])  # Adjusted column layout
    with col2:
        st.pyplot(fig)

    # 5. Comparison Chart
    st.write("### Comparison Chart: Close Prices by Indices")
    comparison_data = data.groupby(['index', 'date'])['close'].mean().reset_index()
    fig_comparison = go.Figure()
    for index in comparison_data['index'].unique():
        index_data = comparison_data[comparison_data['index'] == index]
        fig_comparison.add_trace(go.Scatter(x=index_data['date'], y=index_data['close'], mode='lines', name=index))
    fig_comparison.update_layout(
        title='Comparison of Close Prices Across Indices',
        xaxis_title='Date',
        yaxis_title='Close Price',
        template='plotly_dark'
    )
    st.plotly_chart(fig_comparison, use_container_width=True)

else:
    st.error("No data fetched from Athena. Check your query or connection.")
