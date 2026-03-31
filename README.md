🌦️ Weather Data Analysis Dashboard
📍 Chennai, Tamil Nadu, India
📌 Overview

This project performs real-time weather data analysis using statistical methods and visualizations. It automatically detects the user’s location, fetches 7-day hourly weather data, and generates a comprehensive statistical report along with a multi-panel dashboard.

📸 Project Output

🚀 Features
📍 Auto Location Detection using IP
🌐 Real-time Weather Data (Open-Meteo API)
📊 Statistical Analysis
Mean, Median, Mode
Standard Deviation & Variance
Skewness & Kurtosis
🔗 Correlation Analysis (Pearson)
📈 Linear Regression Model
⚠️ Outlier Detection (Z-score)
📅 Daily Aggregated Insights
🎨 5-Panel Visualization Dashboard
📊 Visualizations Included
7-Day Temperature Trend (with rolling mean & regression)
Daily Mean Temperature Bar Chart
Temperature Distribution (Histogram + Normal Curve)
Temperature Box Plot (per day)
Temperature vs Humidity (Scatter + Regression)
🧠 Statistical Engine

The project computes a complete statistical report using custom logic implemented in
👉

It includes:

Descriptive statistics
Correlation strength & significance
Regression modeling
Outlier detection
⚙️ How It Works

The entire pipeline is handled in
👉

Workflow:

Detect user location
Fetch weather data
Compute statistics
Generate report
Render charts
🌐 Data Source
Open-Meteo API (No API key required)
Configured in
👉
📦 Installation
pip install -r requirements.txt

Dependencies listed in
👉

▶️ Run the Project
python main.py
📁 Project Structure
Weather-Data-Analysis/
│── main.py                # Entry point  
│── weather_api.py         # Fetch weather data  
│── statistics_engine.py   # Statistical computations  
│── visualizer.py          # Dashboard generation  
│── report.py              # Console report  
│── location.py            # IP-based location detection  
│── config.py              # Config & constants  
│── requirements.txt       # Dependencies  
📈 Key Insights (from your output)
Temperature shows a steady increasing trend over the week
Strong negative correlation between temperature & humidity
Data approximately follows a normal distribution
No extreme outliers detected
High regression accuracy (R² ≈ 0.91)
💡 Learning Outcomes
Real-world data handling & API integration
Application of statistical concepts
Data visualization using Matplotlib
Building end-to-end data pipelines
🔮 Future Improvements
Add multi-city comparison
Build a web dashboard (React + Flask)
Add ML-based weather prediction
📜 License

This project is for academic and educational use.
