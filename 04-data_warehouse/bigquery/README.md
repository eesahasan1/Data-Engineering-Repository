# bq sql queries

-- Creating a non-partitioned table
```sql
CREATE OR REPLACE TABLE radiant-psyche-403018.ny_taxi.yellow_taxi_data_non_partitioned AS
SELECT * FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data;
```
-- Creating a partitioned table
```sql
CREATE OR REPLACE TABLE radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT * FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data;
```sql
-- Non partioned vs partitioned processing size
-- non-partioned
```sql
SELECT DISTINCT(VendorID)
FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data_non_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-30';
```
-- partioned
```sql
SELECT DISTINCT(VendorID)
FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-30';
```
-- Output partition data
```sql
SELECT table_name, partition_id, total_rows
FROM `radiant-psyche-403018.ny_taxi.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_taxi_data_partitioned'
ORDER BY total_rows DESC;
```
-- Creating a partitioned and clustered table
```sql
CREATE OR REPLACE TABLE radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned_clustered
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT * FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data;
```
-- Partitioned vs partitioned and clustered processing size
-- partitioned
```sql
SELECT count(*) as trips
FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-30'
  AND VendorID=1;
```
-- partitioned and clustered
```sql
SELECT count(*) as trips
FROM radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned_clustered
WHERE DATE(tpep_pickup_datetime) BETWEEN '2021-01-01' AND '2021-01-30'
  AND VendorID=1;
```

# bq ml queries
```sql
-- SELECT THE COLUMNS INTERESTED FOR YOU
SELECT passenger_count, trip_distance, PULocationID, DOLocationID, payment_type, fare_amount, tolls_amount, tip_amount
FROM `radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned` WHERE fare_amount != 0;
```
-- CREATE A ML TABLE WITH APPROPRIATE TYPE
```sql
CREATE OR REPLACE TABLE `radiant-psyche-403018.ny_taxi.yellow_taxi_data_ml` (
`passenger_count` INTEGER,
`trip_distance` FLOAT64,
`PULocationID` STRING,
`DOLocationID` STRING,
`payment_type` STRING,
`fare_amount` FLOAT64,
`tolls_amount` FLOAT64,
`tip_amount` FLOAT64
) AS (
SELECT passenger_count, trip_distance, cast(PULocationID AS STRING), CAST(DOLocationID AS STRING),
CAST(payment_type AS STRING), fare_amount, tolls_amount, tip_amount
FROM `radiant-psyche-403018.ny_taxi.yellow_taxi_data_partitioned` WHERE fare_amount != 0
);
```
-- CREATE MODEL WITH DEFAULT SETTING
```sql
CREATE OR REPLACE MODEL `radiant-psyche-403018.ny_taxi.tip_model`
OPTIONS
(model_type='linear_reg',
input_label_cols=['tip_amount'],
DATA_SPLIT_METHOD='AUTO_SPLIT') AS
SELECT
*
FROM
`radiant-psyche-403018.ny_taxi.yellow_taxi_data_ml`
WHERE
tip_amount IS NOT NULL;
```
-- CHECK FEATURES
```sql
SELECT * FROM ML.FEATURE_INFO(MODEL `radiant-psyche-403018.ny_taxi.tip_model`);
```
-- EVALUATE THE MODEL
```sql
SELECT
*
FROM
ML.EVALUATE(MODEL `radiant-psyche-403018.ny_taxi.tip_model`,
(
SELECT
*
FROM
`radiant-psyche-403018.ny_taxi.yellow_taxi_data_ml`
WHERE
tip_amount IS NOT NULL
));
```
-- PREDICT THE MODEL
```sql
SELECT
*
FROM
ML.PREDICT(MODEL `radiant-psyche-403018.ny_taxi.tip_model`,
(
SELECT
*
FROM
`radiant-psyche-403018.ny_taxi.yellow_taxi_data_ml`
WHERE
tip_amount IS NOT NULL
));
```
-- PREDICT AND EXPLAIN
```sql
SELECT
*
FROM
ML.EXPLAIN_PREDICT(MODEL `radiant-psyche-403018.ny_taxi.tip_model`,
(
SELECT
*
FROM
`radiant-psyche-403018.ny_taxi.yellow_taxi_data_ml`
WHERE
tip_amount IS NOT NULL
), STRUCT(3 as top_k_features));
```
-- HYPER PARAM TUNNING
```sql
CREATE OR REPLACE MODEL `radiant-psyche-403018.ny_taxi.tip_hyperparam_model`
OPTIONS
(model_type='linear_reg',
input_label_cols=['tip_amount'],
DATA_SPLIT_METHOD='AUTO_SPLIT',
num_trials=5,
max_parallel_trials=2,
l1_reg=hparam_range(0, 20),
l2_reg=hparam_candidates([0, 0.1, 1, 10])) AS
SELECT
*
FROM
`radiant-psyche-403018.ny_taxi.yellow_taxi_data_ml`
WHERE
tip_amount IS NOT NULL;
```

# pushing ml model to docker with tensorflow
* gcloud auth login
* bq --project_id radiant-psyche-403018 extract -m ny_taxi.tip_model gs://ny_taxi_ml_model_403018/tip_model
* mkdir /tmp/model
* gsutil cp -r gs://ny_taxi_ml_model_403018/tip_model /tmp/model
* mkdir -p serving_dir/tip_model/1
* cp -r /tmp/model/tip_model/* serving_dir/tip_model/1

--- not compatible with arm architecutre so Im running it on linux vm from gcp

docker pull tensorflow/serving


docker run -p 8501:8501 --mount type=bind,source=$(pwd)/serving_dir/tip_model,target=/models/tip_model -e MODEL_NAME=tip_model -t tensorflow/serving &

curl -d '{"instances": [{"passenger_count":1, "trip_distance":12.2, "PULocationID":"193", "DOLocationID":"264", "payment_type":"2","fare_amount":20.4,"tolls_amount":0.0}]}' -X POST http://localhost:8501/v1/models/tip_model:predict
http://localhost:8501/v1/models/tip_model