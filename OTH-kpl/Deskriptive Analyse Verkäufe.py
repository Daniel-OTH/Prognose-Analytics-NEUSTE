#%%
import pandas as pd
#%%
import matplotlib.pyplot as plt
#%% 
from pandas.plotting import autocorrelation_plot
#%%
from statsmodels.tsa.seasonal import seasonal_decompose
#%%
from statsmodels.tsa.stattools import adfuller
#%%
from scipy.stats import zscore
#%%
import seaborn as sns
#%%
from datetime import timedelta
#%%
import warnings
#%%
warnings.filterwarnings("ignore")



#%%
# Daten laden
df = pd.read_csv("Data Dataanalysis/sales_data_with_products.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp').sort_index()



#%%
# 1. Überblick   
# 1.1 Tabelle
print("🧾 Erste und letzte Datenzeile:")
print(df.head(1), "\n")
print(df.tail(1), "\n")

print("📉 Fehlende Werte:")
print(df.isnull().sum(), "\n")

# Basisstatistik
columns_to_describe = ['amount', 'product_a', 'product_b', 'product_c']
basisstatistik = df[columns_to_describe].describe()
print("📊 Basisstatistik für Gesamtverkäufe und Produkte A, B, C:\n")
print(basisstatistik)

# 1.2 Boxplots 
# Spalten für Boxplot
columns = ['amount', 'product_a', 'product_b', 'product_c']

# Figure mit 1x4 Subplots anlegen
fig, axes = plt.subplots(nrows=1, ncols=4, figsize=(16, 4))

# Für jede Spalte einen Boxplot zeichnen
for ax, col in zip(axes, columns):
    df[col].plot.box(ax=ax)
    ax.set_title(col.upper())
    ax.set_ylabel("Verkaufsmenge")

plt.suptitle("Boxplots: Gesamt und Produkte A, B, C")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()



#%%
# 2 Monatliche & Wöchentliche Aggregation
# 2.1 Gesamt
# CSV laden und Index setzen
df = pd.read_csv("Data Dataanalysis/sales_data_with_products.csv")  # Pfad ggf. anpassen
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp').sort_index()

# Monatliche Verkäufe
monthly = df['amount'].resample('M').sum()
monthly.index = monthly.index.strftime('%Y-%m')  # Nur Jahr-Monat anzeigen
monthly.plot(kind='bar', figsize=(14, 4), title="📅 Monatliche Gesamtverkäufe", color='skyblue', edgecolor='black')
plt.xlabel("Monat")
plt.ylabel("Verkäufe")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Wöchentliche Verkäufe
weekly = df['amount'].resample('W').sum()
weekly.index = weekly.index.strftime('%Y-%m-%d')  # Nur Datum anzeigen
weekly.plot(figsize=(14, 4), title="📆 Wöchentliche Gesamtverkäufe", color='lightgreen', linewidth=2)
plt.xlabel("Woche")
plt.ylabel("Verkäufe")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# 2.2 Monatliche & Wöchentliche Aggregation je Produkt
monthly_products = df[['product_a', 'product_b', 'product_c']].resample('M').sum()
monthly_products.index = monthly_products.index.strftime('%Y-%m')  # Nur Jahr-Monat anzeigen
monthly_products.plot(kind='bar', figsize=(14, 5), title="📅 Monatliche Verkäufe je Produkt", edgecolor='black')
plt.xlabel("Monat")
plt.ylabel("Verkäufe")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# Wöchentliche Verkäufe je Produkt
weekly_products = df[['product_a', 'product_b', 'product_c']].resample('W').sum()
weekly_products.index = weekly_products.index.strftime('%Y-%m-%d')  # Nur Datum anzeigen
weekly_products.plot(figsize=(14, 5), title="📆 Wöchentliche Verkäufe je Produkt", linewidth=2)
plt.xlabel("Woche")
plt.ylabel("Verkäufe")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()



#%%
# 3 Produktanteile
# 3.1 Gesamt
df[['product_a', 'product_b', 'product_c']].sum().plot(
    kind='pie', autopct='%1.1f%%', title="Gesamtanteil der Produkte", ylabel="")
plt.tight_layout()
plt.show()

# 3.2 Letztes Jahr & letzter Monat
# Aktuellster Zeitpunkt im Datensatz
latest_date = df.index.max()

# Zeiträume definieren
one_year_ago = latest_date - timedelta(days=365)
one_month_ago = latest_date - timedelta(days=30)

# Daten filtern
df_last_year = df[df.index >= one_year_ago]
df_last_month = df[df.index >= one_month_ago]

# Summen berechnen
sum_last_year = df_last_year[['product_a', 'product_b', 'product_c']].sum()
sum_last_month = df_last_month[['product_a', 'product_b', 'product_c']].sum()

# Kreisdiagramm – Letztes Jahr
plt.figure(figsize=(6, 6))
sum_last_year.plot(kind='pie', autopct='%1.1f%%', title="Produktanteile – Letztes Jahr", ylabel="")
plt.tight_layout()
plt.show()

# Kreisdiagramm – Letzter Monat
plt.figure(figsize=(6, 6))
sum_last_month.plot(kind='pie', autopct='%1.1f%%', title="Produktanteile – Letzter Monat", ylabel="")
plt.tight_layout()
plt.show()



#%%
# 4. Rolling Mean / Std-Abweichung
# 4.1 Gesamt
df['rolling_mean_30'] = df['amount'].rolling(window=30).mean()
df['rolling_std_30'] = df['amount'].rolling(window=30).std()

df[['amount', 'rolling_mean_30']].plot(figsize=(12, 4), title="Verkäufe mit 30-Tage-Rolling Mean")
plt.tight_layout()
plt.show()

df[['rolling_std_30']].plot(figsize=(12, 4), title="30-Tage-Rolling Standardabweichung")
plt.tight_layout()
plt.show()

# 4.2 Produkte separat 
# Gleitender 30-Tage-Mittelwert und Standardabweichung berechnen
for product in ['product_a', 'product_b', 'product_c']:
    df[f'{product}_rolling_mean_30'] = df[product].rolling(window=30).mean()
    df[f'{product}_rolling_std_30'] = df[product].rolling(window=30).std()

# Rolling Mean Diagramm
df[[f'{p}_rolling_mean_30' for p in ['product_a', 'product_b', 'product_c']]].plot(
    figsize=(14, 4), title="30-Tage-Rolling Mean für Produkte A, B, C")
plt.xlabel("Datum")
plt.ylabel("Ø Verkäufe")
plt.tight_layout()
plt.show()

# Rolling Std-Abweichung Diagramm
df[[f'{p}_rolling_std_30' for p in ['product_a', 'product_b', 'product_c']]].plot(
    figsize=(14, 4), title="30-Tage-Rolling Standardabweichung für Produkte A, B, C")
plt.xlabel("Datum")
plt.ylabel("Standardabweichung")
plt.tight_layout()
plt.show()

#%%
# 5. Autokorrelationsplot
# 5.1 Gesamt
plt.figure(figsize=(10, 4))
autocorrelation_plot(df['amount'])
plt.title("Autokorrelation der Gesamtverkäufe")
plt.tight_layout()
plt.show()

# 5.2 Produkte separat
for product in ['product_a', 'product_b', 'product_c']:
    plt.figure(figsize=(10, 4))
    autocorrelation_plot(df[product])
    plt.title(f"Autokorrelation – {product.upper()}")
    plt.xlabel("Tage Verzögerung (Lag)")
    plt.ylabel("Korrelation")
    plt.tight_layout()
    plt.show()



#%%
# 6. Saisonale Zerlegung
# 6.1 Gesamt
decomposition = seasonal_decompose(df['amount'], model='additive', period=30)
decomposition.plot()
plt.tight_layout()
plt.show()

# 6.2 Produkte separat
for product in ['product_a', 'product_b', 'product_c']:
    result = seasonal_decompose(df[product], model='additive', period=30)
    result.plot()
    plt.suptitle(f"Saisonale Zerlegung – {product.upper()}", fontsize=14)
    plt.tight_layout()
    plt.show()



#%%
# 7. Stationaritätstest
def test_stationarity(series, name):
    result = adfuller(series.dropna())
    print(f"🧪 ADF-Test – {name}:")
    print(f"  ADF-Statistik: {result[0]:.4f}")
    print(f"  p-Wert:         {result[1]:.4f}")
    print("  ✅ Stationär\n" if result[1] < 0.05 else "  ❌ Nicht stationär\n")

# Gesamtverkäufe
test_stationarity(df['amount'], "Gesamtverkäufe")

# Je Produkt
for product in ['product_a', 'product_b', 'product_c']:
    test_stationarity(df[product], product.upper())



#%%
# 8. Wochentagsanalyse
df['weekday'] = df.index.dayofweek
weekday_avg = df.groupby('weekday')[['product_a', 'product_b', 'product_c']].mean()
weekday_avg.plot(kind='bar', figsize=(10, 4), title="Ø Verkäufe pro Produkt nach Wochentag")
plt.xticks(ticks=range(7), labels=["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"], rotation=0)
plt.tight_layout()
plt.show()



#%%
# 9. Ausreißer 
# 9.1 Ausreißer erkennen (Z-Score)

# Spalten, für die wir Ausreißer zählen wollen
columns = ['amount', 'product_a', 'product_b', 'product_c']

# Z-Score berechnen und Ausreißer zählen
for col in columns:
    df[f'{col}_zscore'] = zscore(df[col].dropna())
    outliers = df[df[f'{col}_zscore'].abs() > 3]
    print(f"🚨 Anzahl Ausreißer für {col}: {len(outliers)}")

# 9.2 Ausreißer visualisieren
# Spalten, die geplottet werden sollen
columns = ['amount', 'product_a', 'product_b', 'product_c']

# Z-Score für jede Serie berechnen
for col in columns:
    df[f'{col}_zscore'] = zscore(df[col].dropna())

# Plot für jede Serie
for col in columns:
    plt.figure(figsize=(12, 4))
    # gesamte Zeitreihe als Linie
    plt.plot(df.index, df[col], label=col, linewidth=1)
    
    # Ausreißer finden
    outliers = df[df[f'{col}_zscore'].abs() > 3]
    
    # Ausreißer als rote Punkte einzeichnen
    plt.scatter(outliers.index, outliers[col], 
                color='red', label='Ausreißer', zorder=5)
    
    plt.title(f"Zeitreihe & Ausreißer – {col}")
    plt.xlabel("Datum")
    plt.ylabel("Verkaufsmenge")
    plt.legend()
    plt.tight_layout()
    plt.show()



#%%
# 10. Produkt-Korrelation
correlation = df[['product_a', 'product_b', 'product_c']].corr()
print("\n🔗 Korrelation zwischen den Produkten:\n", correlation)

sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title("Korrelationsmatrix der Produkte A, B, C")
plt.tight_layout()
plt.show()