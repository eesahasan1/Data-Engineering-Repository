# Setting up a postgreSQL database in docker and ingesting data

## This guide outlines the process for setting up a PostgreSQL database in a Docker container and ingesting data for analysis.

### Prerequisites
- Docker installed and running
- Basic knowledge of command-line interfaces and Docker commands

### Running a PostgreSQL Docker Container

Run the following command in the terminal to pull and run the PostgreSQL container:
```bash
docker run -d \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
postgres:13
```
- `docker run -d` runs the container in the background allowing you to still use the command interface
- for an interactive session, use: 
```
docker run -it
```

### Connecting to the PostgreSQL Database using `pgcli`

Ensure that pgcli is installed:
- For command line interface use:
```bash
!pip install pgcli
```
- In python or jupyter environment, use:
```bash
pip install pgcli
```
Follow the steps outlined in this notebook to batch transfer the data into the PostgresSQL database:
[data-upload-to-postgres](data-upload-to-postgres.ipynb)

**Data Source:**
> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- Select January 2023 dropdown > (2023 January, "Yellow Taxi Trip Records")
- Or directly download the file using the this link:
> https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet


Run this command to connect to the PostgreSQL database:
```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi 
```
![Image](data/images/terminal.png)

#
### Running pgAdmin in a Docker Container
**To manage the PostgreSQL database through a web interface, run pgAdmin using this command:**
```bash
docker run -d \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
dpage/pgadmin4
```
- Access pgAdmin by navigating to "localhost:8080" in a web browser and log in using the specified email and password.
#

### Networking
Create a Docker network to facilitate communication between PostgreSQL database and pgAdmin:
```bash
docker network create pg-network
```

### Connecting PostgreSQL and pgAdmin on the Same Network

Reconfigure both services to add them to the network

PostgreSQL Database with Network Configuration:
```bash
docker run -it \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
--network=pg-network \
--name pg-database \
postgres:13
```

pgAdmin with Network Configuration:
```bash
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
--network=pg-network \
--name pgadmin \
dpage/pgadmin4
```
- Container naming (--name) helps in identifying and managing containers, especially when handling multiple instances.
#
### Alternative method to interact with the PostgreSQL database can be found here: [jupyter-to-postgres-connection.ipynb](jupyter-to-postgres-connection.ipynb)
#

### Convert a Jupyter Notebook to a Script to Run in Cli
```bash
jupyter nbconvert --to=script data-upload-to-postgres.ipynb
```

### Automating Data Ingestion
The script [automating-data-ingestion](automating-data-ingestion.py) demonstrates how to automate the data ingestion process
```bash
python automating-data-ingestion.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_data \
  --url=${URL}
```

### Building and Running a Dockerized Data Ingestion Script
To dockerize the data ingestion script, a Dockerfile is used to define the environment, dependencies, and the script execution. The Dockerfile can be found at [Dockerfile](Dockerfile).

Run the following command to build the Docker image based on the Dockerfile:
```bash
docker build -t taxi_ingest:v001 .
```
- The "." signifies the current directory, indicating where Docker should look for the Dockerfile.

### Executing the Data Ingestion Container
First, set the URL in your command line:
```bash
URL=https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet
```
Then, run the Docker container:
```bash
docker run -it \
  --network=pg-network \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pg-database \
    --port=5432 \
    --db=ny_taxi \
    --table_name=yellow_taxi_data \
    --url=${URL}
```
