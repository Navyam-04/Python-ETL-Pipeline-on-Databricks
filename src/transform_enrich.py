import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time

print("--- Starting Transform & Enrich Phase ---")

# 1. Read the raw data from the Bronze table created in the first notebook
sales_df = spark.read.table("sales_bronze").toPandas()
print("Successfully read data from 'sales_bronze' table.")

# --- Transformation Step 1: Cleaning Sales Data ---
sales_df.columns = sales_df.columns.str.lower().str.replace(' ', '_')
sales_df.fillna(value={"unit_sales": 0}, inplace=True)
sales_df.dropna(subset=['dollar_sales'], inplace=True)
sales_df['date'] = pd.to_datetime(sales_df['date'], format='mixed')
sales_df['unit_sales'] = sales_df['unit_sales'].astype(int)
sales_df['promotion_flag'] = sales_df['promotion_flag'].astype(bool)
sales_df['store_zip'] = sales_df['store_zip'].str.replace('XX', '00')
sales_df['rev_per_unit'] = (sales_df['dollar_sales'] / sales_df['unit_sales']).round(2)
sales_df.replace([np.inf, -np.inf], 0, inplace=True)
print("Data cleaning and feature engineering complete.")

# --- Transformation Step 2: Enriching with Weather Data ---
print("Fetching weather data from API...")
API_KEY = "5883b9ac08253fbd080c073b1832a6a8"
LAT, LON = 34.0522, -118.2437
weather_data = []
unique_dates = sales_df['date'].dt.date.sort_values().unique()

for date_obj in unique_dates:
    try:
        unix_timestamp = int(datetime.combine(date_obj, datetime.min.time()).timestamp())
        url = (f"https://api.openweathermap.org/data/3.0/onecall/timemachine"
               f"?lat={LAT}&lon={LON}&dt={unix_timestamp}&appid={API_KEY}&units=imperial")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather_data.append({"date": date_obj, "temp": data["data"][0]["temp"], "humidity": data["data"][0]["humidity"]})
    except requests.exceptions.RequestException as e:
        print(f"Warning: API call failed for {date_obj}: {e}")
    time.sleep(0.5)

weather_df = pd.DataFrame(weather_data)
weather_df['date'] = pd.to_datetime(weather_df['date'])
final_df = pd.merge(sales_df, weather_df[['date', 'temp']], how="left", on="date")
print("Successfully enriched data with weather information.")

# --- Save to a "Silver" table ---
final_spark_df = spark.createDataFrame(final_df)
(final_spark_df.write
 .format("delta")
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable("sales_silver"))

print("Successfully transformed data and saved to the 'sales_silver' table.")
