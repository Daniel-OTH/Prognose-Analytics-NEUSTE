#%% 
import sqlite3
# %%
import pandas as pd

# %%
csv_customer = pd.read_csv("Data Dataanalysis/customer_information.csv", sep=",", encoding="latin-1")
#%%
csv_arbeitsplan = pd.read_csv("Data Dataanalysis/arbeitsplan_mit_schichtsystem.csv", sep=",", encoding="latin-1")
# %%
csv_sales_1 = pd.read_csv("Data Dataanalysis/sales_data_jan2022_to_now.csv", sep=",", encoding="latin-1")
# %%
csv_sales_multi = pd.read_csv("Data Dataanalysis/sales_data_multi_customers_per_day.csv", sep=",", encoding="latin-1")
# %%
csv_sales_products = pd.read_csv("Data Dataanalysis/sales_data_with_products.csv", sep=",", encoding="latin-1")



# %%
con = sqlite3.connect('data_dataanalysis.db')



# %%
csv_customer.to_sql("customer", con, if_exists="replace", index=False)
# %%
csv_arbeitsplan.to_sql("arbeitsplan", con, if_exists="replace", index=False)
#%%
csv_sales_1.to_sql("sales_1", con, if_exists="replace", index=False)
#%%
csv_sales_multi.to_sql("sales_multi", con, if_exists="replace", index=False)
#%%
csv_sales_products.to_sql("sales_products", con, if_exists="replace", index=False)

# %%
