# Setting up a PostgreSQL Database in Docker for Ingesting data and Data Analysis

## This project outlines the process for setting up a PostgreSQL database in a Docker container and ingesting data for analysis.

### Prerequisites
- Docker installed and running
- Basic knowledge of command-line interfaces, Docker commands, and pandas

## Running a PostgreSQL Docker Container

Run the following command in cli to start a PostgreSQL container:
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
- For an interactive session, replace `-d` with `-it`

**Breakdown:**
```bash
# Run a Docker container in detached mode (in the background)
docker run -d \

# Set the POSTGRES_USER environment variable inside the container to "root"
-e POSTGRES_USER="root" \

# Set the POSTGRES_PASSWORD environment variable inside the container to "root"
-e POSTGRES_PASSWORD="root" \

# Set the POSTGRES_DB environment variable to create a database named "ny_taxi" upon container startup
-e POSTGRES_DB="ny_taxi" \

# Mount a volume from the host system to the container. 
# "$(pwd)/ny_taxi_postgres_data" is the local directory (relative to the current working directory)
# "/var/lib/postgresql/data" is the container's directory where PostgreSQL stores its data.
# This ensures data persistence across container restarts.
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \

# Map port 5432 on the host to port 5432 in the container.
# This allows you to connect to the PostgreSQL server running inside the container using the host's port 5432.
-p 5432:5432 \

# Specify the Docker image to use: "postgres:13", which is version 13 of the official PostgreSQL image.
postgres:13

```
## Connecting to the PostgreSQL Database using `pgcli`
Install pgcli for a command-line interface experience

1. Installing pgcli: 
- In a terminal:
```bash
pip install pgcli
```
- In python or jupyter environment:
```bash
!pip install pgcli
```

2. Batch data transfer
- The steps are outlined in this notebook to batch transfer the data into the PostgresSQL database:
[data-upload-to-postgres](data-upload-to-postgres.ipynb)

> **Data Source:**
> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- Select January 2023 dropdown > (2023 January, "Yellow Taxi Trip Records")
- Or, use `wget` and paste the following link in cli:
> https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet


3. Connect to pg database from terminal to verify the data was processed 
- Run this command to connect to the PostgreSQL database:
```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi 
```
![Image](data/images/terminal.png)

## Running pgAdmin in a Docker Container

To manage the PostgreSQL database through a web interface, start pgAdmin using this command:
```bash
docker run -d \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
dpage/pgadmin4
```

- Access pgAdmin by navigating to "localhost:8080" in a web browser and log in using the specified credentials.


## Docker Networking

Create a Docker network to facilitate communication between PostgreSQL database and pgAdmin:
```bash
docker network create pg-network
```

## Connecting PostgreSQL and pgAdmin on the Same Network

Reconfigure both services to add them to the network

PostgreSQL DB container with network configuration:
```bash
docker run -d \
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


**Alternative method to interact with the PostgreSQL database can be found here:** [jupyter-to-postgres-connection.ipynb](jupyter-to-postgres-connection.ipynb)


## Automating Data Ingestion
1. Convert Jupyter Notebook to python script in cli for automation:
```bash
jupyter nbconvert --to=script data-upload-to-postgres.ipynb
```
2. Designing the automation python script:

- The [automating-data-ingestion](automating-data-ingestion.py) script automates the process of downloading data and ingesting it into a PostgreSQL database

- The script downloads data from a provided URL.
- It supports .csv and .parquet file formats for ingestion.
- Utilizes pandas for data handling and sqlalchemy for database interaction.
- Employs command-line arguments for database connection details and data source URL.

3. Execute the Automation Script

- Run the script with the necessary parameters to start the data ingestion process:

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
- Ensure to replace ${URL} with the actual URL of your data source.

**Breakdown:**
# Executes the data ingestion script with specified parameters
```bash
python automating-data-ingestion.py \
  --user=root \                 # Database username
  --password=root \             # Database password
  --host=localhost \            # Database host address
  --port=5432 \                 # Database port
  --db=ny_taxi \                # Database name to connect to
  --table_name=yellow_taxi_data \ # Target table for data ingestion
  --url=${URL}                  # Data source URL
```

## Dockerizing the Data Ingestion Script
To dockerize the data ingestion script, a Dockerfile is used to define the environment, dependencies, and the script execution. 

**The original Dockerfile without comments can be found here:** [Dockerfile](Dockerfile)

```Dockerfile
FROM python:3.11.4 
"
This line sets the base image for the Docker container: Python Docker image tagged with version 3.11.4
"

RUN pip install pandas sqlalchemy psycopg2 pyarrow requests
"
This command runs inside the container when it's initiated
It's used to install several Python libraries:

pandas: A data manipulation and analysis library.
sqlalchemy: A SQL toolkit and Object-Relational Mapping (ORM) library.
psycopg2: A PostgreSQL database adapter for Python.
pyarrow: Provides Python bindings to the Apache Arrow data format.
requests: A library for making HTTP requests.
"

WORKDIR /app 
"
This instruction sets the working directory in the container to "/app". 
All subsequent commands will be run from this directory. 
If the directory does not exist, it will be created.
"

COPY automating-data-ingestion.py automating-data-ingestion.py
"
This line copies the automating-data-ingestion.py file from the local machine into the container and is placed in the containers working directory "/app", as set by the previous WORKDIR instruction.
"

ENTRYPOINT [ "python", "automating-data-ingestion.py"]
"
Specifies the command to be executed when the container starts. 
In this case, it's executing the Python script "automating-data-ingestion.py" with Python. 
Essentially, when the container starts, it will run "python" and the script "automating-data-ingestion.py"
"
```

Run the following command to build the Docker image based on the Dockerfile just created:
```bash
docker build -t taxi_ingest:v001 . # "taxi_ingest:v001" is the name given to the image
```
- The "." signifies the current directory, indicating where Docker should look for the Dockerfile

## Executing the Data Ingestion Container

1. First, set the URL in your command line:
```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
```
2. Then, run a Docker container based on the "taxi_ingest:v001" image:

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
**Breakdown:**
```bash
# Runs a Docker container interactively (-it) allowing you to interact with the container via the terminal.
docker run -it \

# Connects the container to a Docker network named 'pg-network'. Allows the container to communicate with other containers on the same network, such as a PostgreSQL database container named 'pg-database'.
  --network=pg-network \

# Specifies the Docker image to use for the container. In this case, it's using the image tagged as 'taxi_ingest:v001'.
  taxi_ingest:v001 \

# The following are arguments passed to the entry point of the Docker container. 

# Specifies the username to connect to the PostgreSQL database.
    --user=root \

# Specifies the password for the database user.
    --password=root \

# Specifies the hostname of the PostgreSQL database to connect to. Since the container is connected to 'pg-network', it can resolve 'pg-database' as the hostname of another container on the same network that runs the PostgreSQL database.
    --host=pg-database \

# Specifies the port on which the PostgreSQL database is listening. The default PostgreSQL port is 5432, which is used here.
    --port=5432 \

# Specifies the name of the database to connect to within the PostgreSQL server. Here, the database is named 'ny_taxi'.
    --db=ny_taxi \

# Specifies the name of the table within the 'ny_taxi' database where the data should be ingested. The table name is 'yellow_taxi_data'.
    --table_name=yellow_taxi_data \

# Specifies the URL of the data source from which to ingest data. The actual URL should replace '${URL}' when running the command. Or it can be set prior to running the command by running URL='link'
    --url=${URL}
```

## Configuring Multi-Container Applications with docker-compose
Docker Compose YAML files provide an efficient, and standardized way to define, configure, and manage all the components of multi-container Docker applications. 

The original file without comments can be found here: [docker-compose.yaml](docker-compose.yaml)
```
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
     - "./data/ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
     - "5432:5432"
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"
```

**Breakdown:**

```dockerfile
services: 
 # "defines the different containers (services) that make up the  application"
 pgdatabase: 
 "service (container) to be configurated"
   image: postgres:13 
   "Docker image for PostgreSQL version 13"
   environment: 
   "defines environment variables for the container"
     - POSTGRES_USER=root 
     "sets the default user for the PostgreSQL database to 'root'"
     - POSTGRES_PASSWORD=root 
     "sets the default password for the PostgreSQL database to 'root'"
     - POSTGRES_DB=ny_taxi 
     "creates a default database named 'ny_taxi'."
   volumes: 
   "maps a local directory (right of the colon) to the data directory inside the container (left of the colon)"
    - ./data/ny_taxi_postgres_data:/var/lib/postgresql/data:rw 
    "'rw' specifies that both read and write operations are allowed on this volume"
   ports: 
   "maps port 5432 of the container (PostgreSQL's default port) to port 5432 on the host machine."
    - "5432:5432" 
 pgadmin: 
 "the next service (container) to be configurated"
   image: dpage/pgadmin4 
   "official pgAdmin 4 image"
   environment:
     - PGADMIN_DEFAULT_EMAIL=admin@admin.com
     - PGADMIN_DEFAULT_PASSWORD=root
   ports:
    - "8080:80"
```

## SQL Queries
After running the Docker compose file and all the environmental variables and dependencies are set up, all that's left is to begin analyzing the data. 

Sample queries:
![Alt text](data/images/image.png)

![Alt text](data/images/image-1.png)

![Alt text](data/images/image-2.png)