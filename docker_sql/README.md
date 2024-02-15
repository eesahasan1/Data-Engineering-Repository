# Setting up a PostgreSQL Database in Docker for Ingesting data and Data Analysis



## Table of Contents

1. [Project Overview, Objectives, and Key Features](#overview)
2. [Running a PostgreSQL Docker Container](#running-a-postgresql-docker-container)
3. [Connecting to the PostgreSQL Database Using pgcli](#connecting-to-the-postgresql-database-using-pgcli)
4. [Running pgAdmin in a Docker Container](#running-pgadmin-in-a-docker-container)
5. [Connecting PostgreSQL and pgAdmin on the Same Network](#connecting-postgresql-and-pgadmin-on-the-same-network)
6. [Automating Data Ingestion](#automating-data-ingestion)
7. [Dockerizing the Data Ingestion Script](#dockerizing-the-data-ingestion-script)
8. [Executing the Data Ingestion Container](#executing-the-data-ingestion-container)
9. [Configuring Multi-Container Applications with docker-compose](#configuring-multi-container-applications-with-docker-compose)
10. [SQL Queries](#sql-queries)


## Overview
This project is documents the steps to streamline the setup of a PostgreSQL database within a Docker container, facilitating the seamless ingestion and analysis of data. By harnessing the power of Docker, PostgreSQL, and various data engineering tools, this initiative aims to provide a straightforward framework for handling data from extraction to insightful analysis.

### Objectives
- **Simplify Database Setup**: Straightforward method to deploy a PostgreSQL database within a Docker container.
- **Automate Data Ingestion**: Detail the process of automating the transfer of batch data into the PostgreSQL database, supporting a variety of data formats and sources.
- **Facilitate Data Analysis**: Utilize tools like pgcli for command-line access and pgAdmin for web-based management.

### Key Features
- **Dockerized PostgreSQL Database**: Utilize Docker to encapsulate the PostgreSQL database setup, ensuring a consistent and isolated environment simplifying deployment and scalability.
- **Comprehensive Data Ingestion**: Automates the ingestion of data into PostgreSQL from diverse sources, including direct API calls and cloud storage solutions.
- **Integrated Data Management** Incorporate pgcli and pgAdmin into the Docker network, providing versatile interfaces for database interaction and management.



## Running a PostgreSQL Docker Container

Start a PostgreSQL container with the following command:
```bash
docker run -d \
-e POSTGRES_USER="root" \
-e POSTGRES_PASSWORD="root" \
-e POSTGRES_DB="ny_taxi" \
-v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
-p 5432:5432 \
postgres:13
```
- This command runs the container in the background, maps the host's port 5432 to the container's port 5432, and sets up environment variables for the PostgreSQL instance.
- `docker run -d` runs the container in the background allowing you to still use the command interface. For an interactive session, replace `-d` with `-it`

**Breakdown:**
```bash
docker run -d \
# run a Docker container in detached mode (in the background)

-e POSTGRES_USER="root" \
# set the POSTGRES_USER environment variable inside the container to "root"

-e POSTGRES_PASSWORD="root" \
# set the POSTGRES_PASSWORD environment variable inside the container to "root"

-e POSTGRES_DB="ny_taxi" \
# set the POSTGRES_DB environment variable to create a database named "ny_taxi" upon container startup

-v /data/ny_taxi_postgres_data:/var/lib/postgresql/data \
# mount a volume from the host system to the container
# "/data/ny_taxi_postgres_data" is the local directory where PostgreSQL stores its data
# "/var/lib/postgresql/data" is the container's directory where PostgreSQL stores its data
# volumes ensures data persistence across container restarts

-p 5432:5432 \
# map port 5432 on the host to port 5432 in the container
# establishes a connection to the PostgreSQL server running inside the container using the host's port 5432

postgres:13
# specify the Docker image to use: "postgres:13", which is version 13 of the official PostgreSQL image
```



## Connecting to the PostgreSQL Database using `pgcli`
pgcli is a command-line interface for interacting with PostgreSQL databases.

**1. Installing pgcli**
- Running the command in cli:
```bash
pip install pgcli
```
- Or, in python or jupyter environment:
```bash
!pip install pgcli
```

**2. Connect to Postgres Database**
- Run this command to connect to the PostgreSQL database:
```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi 
```

**3. Batch data transfer**
- The steps are outlined in this notebook to batch transfer the data into the PostgresSQL database:
[data-upload-to-postgres](data-upload-to-postgres.ipynb)

> **Data Source:**
> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- Select January 2023 dropdown > (2023 January, "Yellow Taxi Trip Records")
- Or, use `wget` or `curl -o` and paste the following link in cli:
> https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet

**4. Verify Data Ingestion**
- Verify the data was ingested by running `\dt` to display tables

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



## Connecting PostgreSQL and pgAdmin on the Same Network

**1. Docker Networking**

- Create a Docker network to facilitate communication between PostgreSQL database and pgAdmin:
```bash
docker network create pg-network
```

**2. Network Configuration**

Reconfigure both services to add them to the network

- PostgreSQL database:
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

- pgAdmin:
```bash
docker run -it \
-e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
-e PGADMIN_DEFAULT_PASSWORD="root" \
-p 8080:80 \
--network=pg-network \
--name pgadmin \
dpage/pgadmin4
```

- Container naming `--name` helps in identifying and managing containers, especially when handling multiple instances.


> **Alternative method to interact with the PostgreSQL database can be found here:** [jupyter-to-postgres-connection.ipynb](jupyter-to-postgres-connection.ipynb)



## Automating Data Ingestion
Automate the ingestion of data into PostgreSQL using a Python script

1. Convert Jupyter Notebook to a Python Script:
```bash
jupyter nbconvert --to=script data-upload-to-postgres.ipynb
```

2. Developing the Automation Script

    **The script can be found here**: [automating-data-ingestion](automating-data-ingestion.py)

  >- The script automates the process of downloading data from a specified URL and ingests it into the PostgreSQL database.
  >- It supports `.csv` and `.parquet` file formats, however, with minor additions other formats can be handled as well.
  >- Utilizing pandas for data handling and sqlalchemy for database interaction the script is capable of processing large datasets by ingesting data in manageable chunks.
  >- Employs command-line arguments for database connection details and data source URL for increased versatility.



**3. Executing the Script**

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
```bash
python automating-data-ingestion.py \  # tells the shell to execute the Python interpreter and run the script named automating-data-ingestion.py
  --user=root \  # database username
  --password=root \  # database password
  --host=localhost \  # database host address
  --port=5432 \  # database port
  --db=ny_taxi \  # database name to connect to
  --table_name=yellow_taxi_data \  # target table for data ingestion
  --url=${URL}  # data source URL
```



## Dockerizing the Data Ingestion Script
Dockerize the data ingestion script for consistent execution environments. 

1. Create a `Dockerfile` 
- Specify the Python base image, required packages, and the script as the entry point.

```Dockerfile
FROM python:3.11.4 
# This line sets the base image for the Docker container: Python Docker image tagged with version 3.11.4

RUN pip install pandas sqlalchemy psycopg2 pyarrow requests
# This command runs inside the container 
# It's used to install Python libraries:
""" 
- pandas: A data manipulation and analysis library.
- sqlalchemy: A SQL toolkit and Object-Relational Mapping (ORM) library.
- psycopg2: A PostgreSQL database adapter for Python.
- pyarrow: Provides Python bindings to the Apache Arrow data format.
- requests: A library for making HTTP requests.
"""
WORKDIR /app 
# This instruction sets the working directory in the container to "/app". 
# All subsequent commands will be run from this directory. 
# If the directory does not exist, it will be created.

COPY automating-data-ingestion.py automating-data-ingestion.py
# This line copies the automating-data-ingestion.py file from the local machine into the container and is placed in the containers working directory "/app", as set by the previous WORKDIR instruction.

ENTRYPOINT [ "python", "automating-data-ingestion.py"]
# Specifies the command to be executed when the container starts. 
# In this case, it's executing the Python script "automating-data-ingestion.py" with Python. 
# Essentially, when the container starts, it will run "python" and the script "automating-data-ingestion.py"
```

**The original Dockerfile without comments can be found here:** [Dockerfile](Dockerfile)

**2. Build the Docker**

- Run the following command to build an image based on the Dockerfile just created:
```bash
docker build -t taxi_ingest:v001 . # "taxi_ingest:v001" is the name given to the image using (-t)
```
- The "." signifies the current directory, indicating where Docker should look for the Dockerfile



## Executing the Data Ingestion Container
Run the Docker container for data ingestion, specifying the PostgreSQL database details, the image, and the data source URL as command-line arguments.


1. Set the URL in command line:
```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
```
2. Run a Docker container based on the "taxi_ingest:v001" image:

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
docker run -it \
# runs a Docker container interactively (-it) allowing you to interact with the container via the terminal

  --network=pg-network \  
# connects the container to a Docker network 'pg-network'

  taxi_ingest:v001 \
# specifies the Docker image to use for the container. 
#i n this case, it's using the image tagged as 'taxi_ingest:v001'


# The following are arguments passed to the entry point of the Docker container. 
    --user=root \
# specifies the username to connect to the PostgreSQL database

    --password=root \
# specifies the password for the database user

    --host=pg-database \
# specifies the hostname of the PostgreSQL database to connect to. 
# since the container is connected to 'pg-network', it can resolve 'pg-database' as the hostname of another container on the same network that runs the PostgreSQL database

    --port=5432 \
# specifies the port on which the PostgreSQL database is listening

    --db=ny_taxi \
# specifies the name of the database to connect to within the PostgreSQL server


    --table_name=yellow_taxi_data \
# specifies the name of the table within the 'ny_taxi' database where the data should be ingested

    --url=${URL}
# specifies the URL of the data source from where to extract the data
# the actual URL should replace '${URL}' when running the command 
# or can be set prior to running the command by running URL='link'.

```



## Configuring Multi-Container Applications with docker-compose
Docker Compose YAML files provide an efficient, and standardized way to define, configure, and manage all the components of multi-container Docker applications. 

>The original file without comments can be found here: [docker-compose.yaml](docker-compose.yaml)
```yaml
services:
  # Defines a service named 'pgdatabase' which represents a container.
  pgdatabase:
    image: postgres:13  # Specifies the Docker image to use for the container, in this case, PostgreSQL version 13.
    environment:  # Sets environment variables inside the container.
      - POSTGRES_USER=root  # Defines the default username for the PostgreSQL database.
      - POSTGRES_PASSWORD=root  # Sets the password associated with the PostgreSQL user.
      - POSTGRES_DB=ny_taxi  # Specifies the name of the default database to be created upon container startup.
    volumes:
      # Maps a volume from the host to the container, specifying a path on the host to store PostgreSQL data.
      - "./data/ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      # Maps port 5432 on the host to port 5432 in the container, allowing external access to the PostgreSQL server.
      - "5432:5432"
  # Defines another service named 'pgadmin' for the PostgreSQL web administration tool.
  pgadmin:
    image: dpage/pgadmin4  # Specifies the Docker image for pgAdmin 4, a web-based administration tool for PostgreSQL.
    environment:  # Sets environment variables for the pgAdmin container.
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com  # Sets the default email address to log into pgAdmin.
      - PGADMIN_DEFAULT_PASSWORD=root  # Defines the default password for the pgAdmin login.
    ports:
      # Maps port 8080 on the host to port 80 in the container, making pgAdmin accessible via the host's port 8080.
      - "8080:80"
```

## SQL Queries
After running the Docker compose file and all the environmental variables and dependencies are set up, all that's left is to begin analyzing the data.

Sample queries:
![Alt text](data/images/image.png)

![Alt text](data/images/image-1.png)

![Alt text](data/images/image-2.png)