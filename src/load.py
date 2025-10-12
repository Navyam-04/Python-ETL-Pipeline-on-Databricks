print("--- Starting Load Phase ---")

# Read the clean data from the Silver table
silver_df = spark.read.table("sales_silver")

# Save the final data to the "Gold" table
(silver_df.write
 .format("delta")
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable("sales_gold_final"))

print("Successfully loaded data into the final 'sales_gold_final' table.")
print("\n--- ETL Pipeline Finished! ---")

# Display the final table to confirm
display(spark.table("sales_gold_final"))
