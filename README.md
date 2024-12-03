# 📈 Real-Time Stock Market Analysis Dashboard


## Overview
The **Real-Time Stock Market Analysis Dashboard** is an interactive tool designed to visualize, analyze, and explore real-time stock market trends. This project leverages cutting-edge technologies such as **Python**, **AWS Glue**, **Athena**, **Apache Kafka**, and **SQL** to build an end-to-end pipeline for processing and visualizing stock market data.


---

## Demo 🎥

[![Real-Time Stock Market Analysis Demo](stock-market)](https://www.youtube.com/watch?v=szyyI5sOzg4)

Click the GIF above to watch the demo of the App on Youtube or here's the link (https://www.youtube.com/watch?v=szyyI5sOzg4)


---
## Features
- **Real-Time Data Integration**: Streams data using **Apache Kafka** and processes it in real time.
- **Data Transformation**: Structured and cataloged using **AWS Glue**.
- **Efficient Querying**: Fetches data from **AWS Athena** using **SQL** for analysis.
- **Interactive Visualizations**:
  - **Candlestick Charts**: Display stock price movements (open, high, low, close).
  - **Moving Average Charts**: Identify trends with dynamic moving averages.
  - **Correlation Heatmaps**: Visualize relationships between stock metrics.
  - **Comparison Charts**: Benchmark multiple indices over time.
- **Dynamic Dashboards**: Built with **Streamlit** for responsive, user-friendly interfaces.

---

## Technology Stack
### 1. **Python**
   - Core programming language for processing data and creating visualizations.
   - Libraries Used: `pandas`, `plotly`, `seaborn`, `matplotlib`, `streamlit`.

### 2. **Apache Kafka**
   - Simulates real-time stock market data streams.
   - Enables seamless data streaming for real-time analytics.

### 3. **AWS Glue**
   - Transforms raw data into a structured format.
   - Catalogs data for querying in AWS Athena.

### 4. **AWS Athena**
   - Runs SQL queries on structured data stored in S3.
   - Provides quick access to both real-time and historical data.

### 5. **SQL**
   - Query language for fetching and analyzing stock market data.

### 6. **Streamlit**
   - Framework for creating an intuitive, interactive dashboard.
