#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from time import time
import argparse
import requests
import os

def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    
    file_name, file_extension = os.path.splitext(os.path.basename(url))
    
    download_file(params.url, file_name)

    # Check file extension and read file accordingly
    if file_extension == '.parquet':
        # Convert Parquet to DataFrame
        df = pd.read_parquet(file_name)
        # Optional: Convert DataFrame to CSV if needed
        csv_name = file_name.replace('.parquet', '.csv')
        df.to_csv(csv_name, index=False)
        file_to_process = csv_name
    else:
        file_to_process = file_name
    
    # create the connection to postgresql server in docker for data ingestion
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # manually set the dtype to str for col 6 due to pandas data interpretation error
    df = pd.read_csv(file_to_process, dtype={6: 'str'})

    # convert dtypes to datetime values
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # insert the schema and data types without any data to ensure the correct structure
    # if it already exists, it will be replaced
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    # Batch data ingestion into manageable sizes due to large file size
    # manually set the dtype to str for col 6 due to pandas data interpretation error
    df_iter = pd.read_csv(file_to_process, dtype={6: 'str'}, iterator=True, chunksize=100000)

    # infinite loop until StopIteration error (data transfer complete)
    while True:
        try:
            t_start = time()
            
            df = next(df_iter) # fetches the next chunk after each iteration of 100,000 values
        
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        
            df.to_sql(name=table_name, con=engine, if_exists='append') # inserts the chunk of data into the table
        
            t_end = time()
        
            print(f'Inserted {len(df)} rows... took {t_end - t_start:.3f} seconds')
        except StopIteration:
            print("No more data to process.")
            break


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres.')

    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='table name for postgres')
    parser.add_argument('--url', help='file url for postgres')

    args = parser.parse_args()

    main(args)