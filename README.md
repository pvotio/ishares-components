# iShares Components

**iShares Components** is a Python-based data pipeline that automates the collection, transformation, and storage of financial data related to iShares ETFs. It integrates with Microsoft SQL Server, utilizes proxy-enabled scraping (via Bright Data), and supports Docker-based deployment for seamless operation in production environments.

---

## Project Overview

This application performs the following steps:
1. Initializes logging and configuration from environment variables.
2. Runs the main engine (`core.Engine`) which scrapes and fetches raw ETF data.
3. Transforms the fetched data using a `transformer.Agent`.
4. Stores the structured dataset into a specified Microsoft SQL Server table.

---

## Features

- **Scrapes Financial Data**: Gathers iShares ETF data using Bright Data proxies.
- **Transforms Data**: Cleans and structures using pandas and a custom transformer agent.
- **Database Integration**: Inserts final data into a Microsoft SQL Server table.
- **Configurable**: All environment settings are customizable.
- **Docker Support**: Easily deployable using Docker.
- **CI/CD Ready**: Includes Azure DevOps pipeline configuration.

---

## Project Structure

```
ishares-components/
│
├── config/               # Logger and environment settings
├── database/             # DB connections and helpers
├── engine/               # Main scraping and processing logic
├── transformer/          # Transformation logic (Agent)
├── main.py               # Entry point script
├── requirements.txt      # Python dependencies
├── .env.sample           # Sample environment variables
├── Dockerfile            # Docker configuration
├── azure-pipelines.yaml  # Azure DevOps pipeline
```

---

## Requirements

- Python 3.10+
- Microsoft SQL Server
- `msodbcsql18` driver (automatically installed in Docker)
- (Optional) Docker

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/arqs-io/ishares-components.git
cd ishares-components
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy and edit `.env.sample` as `.env`:

```env
# Logging
LOG_LEVEL=INFO

# Output Table
OUTPUT_TABLE=etl.extall_index_components

# Bright Data Proxy Configuration
BRIGHTDATA_PROXY=
BRIGHTDATA_PORT=
BRIGHTDATA_USER=
BRIGHTDATA_PASSWD=

# Microsoft SQL Server Configuration
MSSQL_AD_LOGIN=
MSSQL_SERVER=
MSSQL_DATABASE=
MSSQL_USERNAME=
MSSQL_PASSWORD=
```

### 4. Run the Application

```bash
python main.py
```

---

## Docker Instructions

### Build Docker Image

```bash
docker build -t ishares-components .
```

### Run Docker Container

```bash
docker run --env-file .env ishares-components
```

---

## Application Flow

```text
main.py
│
├── logger + settings loaded from config
├── engine = core.Engine()
│   └── engine.run() → fetch raw data
│
├── data passed to Agent() for transformation
├── transformed DataFrame logged
├── DB connection via init_db_instance()
└── Final data inserted into OUTPUT_TABLE
```

---

## Development

### Code Style

- Uses `flake8` for linting
- Formatted with `black` (see `pyproject.toml`)

```bash
flake8 .
black .
```

---

## Contributing

1. Fork this repo
2. Create a feature branch: `git checkout -b feature-x`
3. Commit your changes
4. Push and open a pull request

---

## License

MIT License — feel free to use, modify, and distribute with attribution.
