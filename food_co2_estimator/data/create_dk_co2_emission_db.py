import os
import sqlite3

import pandas as pd

df = pd.read_excel(
    f"{os.getcwd()}/food_co2_estimator/data/Results_FINAL_20210201v4.xlsx",
    sheet_name="Ra_500food",
)

# Rename columns to database friendly names
df = df.rename(
    columns={
        "Total kg CO2-eq/kg": "Total_kg_CO2_eq_kg",
        "Energi (KJ/100 g)": "Energy",
        "Data sources": "Data_sources",
        "Comments": "Comments",
    }
)
df["Total_kg_CO2_eq_kg"] = df["Total_kg_CO2_eq_kg"].round(2)
df = df.loc[~df["Name"].str.contains("|".join(["Pizza", "Lasagne"]))]  # remove pizza

conn = sqlite3.connect(f"{os.getcwd()}/food_co2_estimator/data/dk_co2_emission.db")

FIELDS = ["Name", "Navn", "Unit", "Total_kg_CO2_eq_kg", "Energy"]
# create database from df file
df[FIELDS].to_sql("dk_co2_emission", conn, if_exists="replace", index=False)

# Test that it works by extracting the first row
c = conn.cursor()
c.execute("SELECT * FROM 'dk_co2_emission' LIMIT 1")
print(c.fetchone())
# count the total number of rows
c.execute("SELECT COUNT(*) FROM 'dk_co2_emission'")
print(c.fetchone())


conn.close()
