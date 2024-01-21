# 1. Have Docker installed

# 2. Run in terminal to build docker image and create the container

docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13

# 3. Run in terminal to connect and interact with postgres db
pgcli -h localhost -p 5432 -u root -d ny_taxi 

# Data used (2023 January, "Yellow Taxi Trip Records")
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page