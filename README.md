# Earthquakes Data Pipeline 🌋

A fully-functioning, end-to-end ETL pipeline and dashboard which cleans, transforms, and analyses real-time event data of earthquakes around the world.

## Introduction 🌷



## Getting Started 🏁

Firstly, you must be signed into AWS. Ensure you have the [aws command line](https://aws.amazon.com/cli/) installed on your local machine, and then run the command `aws login`. This should open an AWS window on your default browser, and you should select the account to authenticate.

## Project Structure 📂🪷

```text
├── pipeline/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
│
└── terraform/
    └── main.tf
```

## Architecture Diagram & ERD 🧩🪷

![ERD Diagram](quake_erd_ver1.png)


## Data Source 📊🌱
The data source from which this pipeline extracts recordings is this [API](https://tools.sigmalabs.co.uk/api/plants/8)

Ⓒ Quakes Group (Basil, Emma, Fariha, Jordan)