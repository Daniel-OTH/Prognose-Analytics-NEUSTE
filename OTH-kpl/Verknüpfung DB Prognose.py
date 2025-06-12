#%%
import sqlite3
import pandas as pd
import os

#%%
# Verzeichnis mit CSV-Dateien
csv_folder = "Data Prognose"

# Verbindung zur SQLite-Datenbank
con = sqlite3.connect("data_dataprognose.db")

#%%
# Hilfsfunktion, um CSV-Dateien zu laden und in SQL zu schreiben
def import_csv_to_sql(filename, tablename):
    path = os.path.join(csv_folder, filename)
    df = pd.read_csv(path, sep=",", encoding="latin-1")
    df.to_sql(tablename, con, if_exists="replace", index=False)

#%%
# Liste aller CSV-Dateien im Ordner
csv_files = [
    "forecast_general_sales.csv",
    "forecast_Gesamt.csv",
    "forecast_growth_comparison.csv",
    "forecast_Kunde_Kunde_002.csv",
    "forecast_Kunde_Kunde_014.csv",
    "forecast_Kunde_Kunde_018.csv",
    "forecast_Kunde_Kunde_048.csv",
    "forecast_Kunde_Kunde_049.csv",
    "forecast_Kunde_Kunde_057.csv",
    "forecast_Kunde_Kunde_078.csv",
    "forecast_Kunde_Kunde_085.csv",
    "forecast_Kunde_Kunde_090.csv",
    "forecast_Kunde_Kunde_101.csv",
    "forecast_product_a.csv",
    "forecast_product_b.csv",
    "forecast_product_c.csv",
    "forecast_Region_Mitte.csv",
    "forecast_Region_Nord.csv",
    "forecast_Region_Süd.csv",
    "forecast_Segment_Automotive.csv",
    "forecast_Segment_Food & Beverage.csv",
    "forecast_Segment_Healthcare.csv",
    "forecast_Segment_IT Services.csv",
    "forecast_Segment_Logistics.csv",
    "forecast_Segment_Manufacturing.csv",
    "forecast_Segment_Retail.csv"
]

# Importiere alle CSV-Dateien in die Datenbank
for file in csv_files:
    table_name = os.path.splitext(file)[0].replace(" ", "_").replace("&", "and")
    import_csv_to_sql(file, table_name)


# Verbindung schließen
con.close()

# %%
