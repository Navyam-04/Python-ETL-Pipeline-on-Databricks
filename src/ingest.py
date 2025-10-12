import pandas as pd
import glob

print("--- Starting Extract Phase ---")

# Create a pattern to find all the daily sales files in your Volume folder
daily_sales_path = "/Volumes/workspace/default/project_files/LA_Retail_Sales_By_Day/*.csv"

# Use glob to get a list of all the file paths
file_paths = glob.glob(daily_sales_path)

# Read and combine all the daily files into a single DataFrame
raw_sales_df = pd.concat((pd.read_csv(f) for f in file_paths), ignore_index=True)

# Convert the pandas DataFrame to a Spark DataFrame to save it
raw_spark_df = spark.createDataFrame(raw_sales_df)

# Save the raw data to a "Bronze" table for the next notebook to use
(raw_spark_df.write
 .format("delta")
 .mode("overwrite")
 .saveAsTable("sales_bronze"))

print(f"Successfully extracted {raw_spark_df.count()} rows into the 'sales_bronze' table.")
