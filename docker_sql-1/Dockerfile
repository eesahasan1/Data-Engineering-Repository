FROM python:3.11.4

RUN pip install pandas sqlalchemy psycopg2 pyarrow requests

WORKDIR /app

COPY automating-data-ingestion.py automating-data-ingestion.py

ENTRYPOINT [ "python", "automating-data-ingestion.py"]
