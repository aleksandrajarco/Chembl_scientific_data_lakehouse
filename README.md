# ChEMBL Scientific Data Lakehouse

A data engineering project that ingests scientific activity data from the ChEMBL REST API, processes and validates the data, and transforms it into analytics-ready Parquet datasets using PySpark.

The project focuses on building a reliable scientific data ingestion pipeline with pagination, retry handling, validation, resumable processing, automated tests, and structured data transformation.

## Project Goals

The goal of this project is to demonstrate an end-to-end data engineering workflow for scientific data:

* ingest data from a public REST API,
* handle pagination and API failures,
* validate incoming data,
* process and transform data with PySpark,
* store processed data in Parquet format,
* support repeatable and testable data processing.
