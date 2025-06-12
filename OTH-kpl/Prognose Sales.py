#%%
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import plot_components_plotly
from datetime import datetime
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

#%%
# Load data
df = pd.read_csv("Data Dataanalysis/sales_data_with_products.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp').sort_index()

#%%
# Function for Prophet Forecast
def prophet_forecast(df, column, periods=500, freq='D', name=None):
    df_prophet = df[[column]].reset_index().rename(columns={'timestamp': 'ds', column: 'y'})

    model = Prophet()
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    # Plot Forecast
    fig = model.plot(forecast)
    plt.title(f"Forecast for {column}")
    plt.axvline(pd.Timestamp(datetime.today().date()), color='red', linestyle='--', label="Today")
    plt.ylim(bottom=0)  # No negative y-axis
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Save forecast
    filename = f"forecast_{name or column}.csv"
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv(filename, index=False)
    print(f"✅ Forecast for {column} saved as {filename}")

    # Show seasonal effects (interactive)
    plot_components_plotly(model, forecast)

    # Highlight seasonal peaks in the forecast period
    try:
        seasonal = forecast[['ds', 'seasonal']].copy()
        seasonal_future = seasonal[seasonal['ds'] > pd.Timestamp.today()]
        threshold = seasonal_future['seasonal'].quantile(0.9)
        peaks = seasonal_future[seasonal_future['seasonal'] > threshold]
        if not peaks.empty:
            print(f"🌞 High seasonal impact expected for {column} around:")
            print(peaks[['ds', 'seasonal']].head(5))
    except KeyError:
        print(f"⚠️ No 'seasonal' component found in forecast for {column}.")

    return forecast

#%%
# 1. General Sales Forecast
forecast_general = prophet_forecast(df, 'amount', name='general_sales')

#%%
# 2. Forecasts for Products A, B, C
for product in ['product_a', 'product_b', 'product_c']:
    try:
        forecast = prophet_forecast(df, product, name=product)
    except Exception as e:
        print(f"❌ Error forecasting {product}: {e}")


#%%
# 3. Compare Forecast with Historical Mean

# Mapping Forecast-Namen zu Original-Spaltennamen
name_map = {
    'general_sales': 'amount',
    'product_a': 'product_a',
    'product_b': 'product_b',
    'product_c': 'product_c'
}

# Forecasts sammeln
forecast_results = {
    'general_sales': forecast_general,
    'product_a': pd.read_csv("forecast_product_a.csv"),
    'product_b': pd.read_csv("forecast_product_b.csv"),
    'product_c': pd.read_csv("forecast_product_c.csv")
}

# Vergleich starten
start_forecast = pd.Timestamp.today()
growth_records = []

print("\n📈 Vergleich mit historischem Durchschnitt:")
for name, forecast in forecast_results.items():
    try:
        original_col = name_map[name]
        actual_mean = df[original_col].mean()
        forecast['ds'] = pd.to_datetime(forecast['ds'])
        future_mean = forecast.loc[forecast['ds'] >= start_forecast, 'yhat'].mean()
        growth = ((future_mean - actual_mean) / actual_mean) * 100
        print(f"🔹 {name}: Ø Prognose = {future_mean:.1f} vs. Historisch = {actual_mean:.1f} ➝ Veränderung: {growth:+.1f}%")
        growth_records.append({
            'name': name,
            'historical_mean': actual_mean,
            'forecast_mean': future_mean,
            'growth_percent': round(growth, 2)
        })
    except Exception as e:
        print(f"⚠️ Fehler bei {name}: {e}")

# Optional: Speichern als CSV
growth_df = pd.DataFrame(growth_records)
growth_df.to_csv("forecast_growth_comparison.csv", index=False)
print("\n📄 Wachstumsauswertung gespeichert als 'forecast_growth_comparison.csv'")

#%%
# 📊 Balkendiagramm: Forecast vs. Historisch
plt.figure(figsize=(10, 6))
bar_width = 0.35
x = range(len(growth_df))

plt.bar(x, growth_df['historical_mean'], width=bar_width, label='Historisch', color='lightgray')
plt.bar([i + bar_width for i in x], growth_df['forecast_mean'], width=bar_width, label='Forecast', color='skyblue')

plt.xticks([i + bar_width / 2 for i in x], growth_df['name'])
plt.ylabel("Ø Verkäufe")
plt.title("Vergleich: Forecast vs. Historische Verkäufe")
plt.legend()
plt.tight_layout()
plt.show()

#%%
# 📈 Liniendiagramm: Prozentuales Wachstum
plt.figure(figsize=(8, 5))
sns.barplot(x='name', y='growth_percent', data=growth_df, palette='coolwarm')
plt.axhline(0, color='black', linestyle='--')
plt.ylabel("Wachstum (%)")
plt.title("Prozentuales Wachstum der Prognose gegenüber dem historischen Durchschnitt")
plt.tight_layout()
plt.show()

# %%
