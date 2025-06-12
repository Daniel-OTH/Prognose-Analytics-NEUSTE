#%%
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

#%%
# 1. Load sales data (NEW file)
df_sales = pd.read_csv("Data Dataanalysis/sales_data_multi_customers_per_day.csv")
df_sales['date'] = pd.to_datetime(df_sales['date'])
df_sales['customer_id'] = df_sales['customer_id'].astype(str)
df_sales = df_sales.sort_values('date')

#%%
# 2. Load customer info (region, branch)
df_customers = pd.read_csv("Data Dataanalysis/customer_information.csv")
df_customers['customer_id'] = df_customers['customer_id'].astype(str)

#%%
# 3. Aggregate total units sold per customer per day
df_customer_sales = df_sales.groupby(['date', 'customer_id'])['units'].sum().reset_index()

#%%
# 4. Merge sales with customer info
df_merged = pd.merge(
    df_customer_sales,
    df_customers[['customer_id', 'region', 'branch']],
    on='customer_id',
    how='left'
)

#%%
# 5. Forecasting function using Prophet
def prophet_forecast_plot(df, date_col='date', value_col='units', periods=400, freq='D', name=None):
    df_prophet = df.rename(columns={date_col: 'ds', value_col: 'y'})[['ds', 'y']].sort_values('ds')

    model = Prophet()
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    # Plot forecast
    plt.figure(figsize=(10, 6))
    plt.plot(df_prophet['ds'], df_prophet['y'], 'b.', label='Historisch')
    plt.plot(forecast['ds'], forecast['yhat'], 'r-', label='Prognose')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='pink', alpha=0.3)
    plt.axvline(datetime.today(), color='black', linestyle='--', label='Heute')
    plt.title(f"Prognose für {name}")
    plt.xlabel('Datum')
    plt.ylim(bottom=0)
    plt.ylabel('Verkaufte Einheiten')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Save forecast
    filename = f"forecast_{name}.csv"
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv(filename, index=False)
    print(f"✅ Prognose gespeichert: {filename}")

    return forecast

#%%
# --- 0. Gesamte Prognose ---
df_total = df_sales.groupby('date')['units'].sum().reset_index()
prophet_forecast_plot(df_total, name="Gesamt")

#%%
# --- 1. Top 10 Kunden-Prognosen ---
top_10_customers = df_customer_sales.groupby('customer_id')['units'].sum().nlargest(10).index.tolist()
print("Top 10 Kunden:", top_10_customers)

for cust_id in top_10_customers:
    df_cust = df_customer_sales[df_customer_sales['customer_id'] == cust_id]
    prophet_forecast_plot(df_cust, name=f"Kunde_{cust_id}")

#%%
# --- 2. Prognose nach Regionen ---
for region in df_merged['region'].dropna().unique():
    df_region = df_merged[df_merged['region'] == region].groupby('date')['units'].sum().reset_index()
    prophet_forecast_plot(df_region, name=f"Region_{region}")

#%%
# --- 3. Prognose nach Branches ---
for branch in df_merged['branch'].dropna().unique():
    df_branch = df_merged[df_merged['branch'] == branch].groupby('date')['units'].sum().reset_index()
    prophet_forecast_plot(df_branch, name=f"Segment_{branch}")

print("🎉 Alle Prognosen wurden erstellt und gespeichert!")