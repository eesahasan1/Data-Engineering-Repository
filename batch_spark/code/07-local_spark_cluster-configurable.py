#!/usr/bin/env python
# coding: utf-8

import argparse

import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


parser = argparse.ArgumentParser()

parser.add_argument('--input_green', required=True)
parser.add_argument('--input_yellow', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

input_green = args.input_green
input_yellow = args.input_yellow
output = args.output

# remove .master config and specify the URL in terminal using --master when creating a pyspark job
spark = SparkSession.builder \
    .appName('test') \
    .getOrCreate()

# "*" wildcard means include all folders within the subdirectories since these tables are partitioned
df_green = spark.read.parquet(input_green)

df_yellow = spark.read.parquet(input_yellow)

df_green.printSchema()

# rename columns
df_green = df_green \
    .withColumnRenamed('lpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('lpep_dropoff_datetime', 'dropoff_datetime')

df_green.columns

df_yellow.printSchema()

df_yellow = df_yellow \
    .withColumnRenamed('tpep_pickup_datetime', 'pickup_datetime') \
    .withColumnRenamed('tpep_dropoff_datetime', 'dropoff_datetime')

df_yellow.columns

# shows the columns that both have in common
set(df_green.columns) & set(df_yellow.columns)

# create a list of column names that are in common
common_columns = []

yellow_columns = set(df_yellow.columns)

for col in df_green.columns:
    if col in yellow_columns:
        common_columns.append(col)

common_columns

from pyspark.sql import functions as F

# appending `service_type` to know what data is from which dataset
df_green_sel = df_green \
    .select(common_columns) \
    .withColumn('service_type', F.lit('green'))

df_yellow_sel = df_yellow \
    .select(common_columns) \
    .withColumn('service_type', F.lit('yellow'))

# combining two spark dataframes into `df_trips_data` 
df_trips_data = df_green_sel.unionAll(df_yellow_sel)

df_trips_data.columns

df_trips_data.groupBy('service_type').count().show()

# create a temporary table to run sql queries
df_trips_data.registerTempTable('trips_data')

spark.sql("""
SELECT
    service_type,
    count(1)
FROM
    trips_data
GROUP BY 
    service_type
""").show()

df_result = spark.sql("""
SELECT 
    -- Reveneue grouping 
    PULocationID AS revenue_zone,
    date_trunc('month', pickup_datetime) AS revenue_month, 
    service_type, 

    -- Revenue calculation 
    SUM(fare_amount) AS revenue_monthly_fare,
    SUM(extra) AS revenue_monthly_extra,
    SUM(mta_tax) AS revenue_monthly_mta_tax,
    SUM(tip_amount) AS revenue_monthly_tip_amount,
    SUM(tolls_amount) AS revenue_monthly_tolls_amount,
    SUM(improvement_surcharge) AS revenue_monthly_improvement_surcharge,
    SUM(total_amount) AS revenue_monthly_total_amount,
    SUM(congestion_surcharge) AS revenue_monthly_congestion_surcharge,

    -- Additional calculations
    AVG(passenger_count) AS avg_montly_passenger_count,
    AVG(trip_distance) AS avg_montly_trip_distance
FROM
    trips_data
GROUP BY
    1, 2, 3
""")

df_result.show()

# write df_results into a single parquet file with `coalesce`

df_result \
    .coalesce(1) \
    .write.parquet(output, mode='overwrite')

