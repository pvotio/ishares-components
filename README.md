# iShares Components

This repository contains an end-to-end **Python ETL pipeline** deployed to **Azure Kubernetes Service (AKS)**. It scrapes key financial data on the constituents of various iShares ETFs, transforms the data, and loads it into an **Azure SQL Database**. The pipeline is orchestrated by workload IDs, uses **Bright Data** as a proxy service for reliable scraping, and is containerized with Docker.

 ![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

## Table of Contents

- [Overview](#overview)
- [Core Workflow](#core-workflow)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Clone the Repository](#clone-the-repository)
  - [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
- [Dockerfile Details](#dockerfile-details)
- [Scheduled Execution](#scheduled-execution)
- [Azure Resources](#azure-resources)
- [CI/CD with Azure Pipelines](#cicd-with-azure-pipelines)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)


## Core Workflow

1. **Initialization**: `main.py` accepts a `WORKLOAD_ID`, sets up logging, and loads configuration.
2. **Scraping**: `ishare.py` retrieves ETF constituent tickers and metadata from iShares, routing HTTP requests through the Bright Data proxy.
3. **Transformation**: `transformer.py` and `utils.py` normalize, enrich, and validate the scraped data.
4. **Loading**: `mssql.py` connects to Azure SQL Database and performs upserts of transformed records.
5. **Containerization**: Dockerfile builds a Docker image based on **Python 3.13.2**, installs dependencies, and sets the ETL command.
6. **Deployment**: Image is pushed to Azure Container Registry (ACR) and deployed on AKS.

## Architecture

1. **Scraping Module**: Fetches data via Bright Data proxy (`ishare.py`).
2. **Transformation Module**: Cleans and formats data (`transformer.py`, `utils.py`).
3. **Database Module**: Interfaces with Azure SQL DB (`mssql.py`).
4. **Orchestration**: `core.py` coordinates module execution by workload ID.
5. **Container & CI/CD**: Built with Docker and deployed via Azure Pipelines.

## Prerequisites

- Python 3.13.2+
- Docker
- Azure CLI
- Azure subscription with permissions to create:
  - AKS cluster
  - Azure SQL Database
  - Azure Container Registry
- `kubectl`

## Getting Started

### Clone the Repository
```bash
git clone https://github.com/your_org/shares-components.git
cd shares-components
```

### Configuration

1. **settings.py**: Update Azure SQL and ACR connection strings.
2. **logger.py**: Configure log levels and handlers.
3. **azure-pipelines.yaml**: Adjust registry connection and image repository variables as needed.

### Environment Variables

The pipeline relies on these environment variables, typically injected via Kubernetes secrets or ConfigMaps:

| Variable             | Description                            |
|----------------------|----------------------------------------|
| `LOG_LEVEL`          | Logging verbosity (e.g., INFO, DEBUG)  |
| `OUTPUT_TABLE`       | Target table in Azure SQL DB          |
| `BRIGHTDATA_USER`    | Bright Data API username              |
| `BRIGHTDATA_PASSWD`  | Bright Data API password              |
| `BRIGHTDATA_PROXY`   | Proxy host (e.g., `brd.superproxy.io`) |
| `BRIGHTDATA_PORT`    | Proxy port (e.g., `33335`)             |
| `MSSQL_AD_LOGIN`     | Enable Azure AD authentication (true)  |
| `MSSQL_SERVER`       | Azure SQL server hostname             |
| `MSSQL_DATABASE`     | Azure SQL database name               |

## Dockerfile Details

- **Base Image**: `python:3.13.2-slim-bullseye`
- **System Dependencies**: Includes ODBC driver (`msodbcsql18`), `mssql-tools`, and Unix ODBC headers.
- **Python Dependencies**: Installs packages from `requirements.txt` without cache.
- **User Context**: Creates a non-root `client` user for security.
- **Command**: Executes `python main.py` with the provided `WORKLOAD_ID`.

## Scheduled Execution

This ETL pipeline is deployed on AKS as a Kubernetes **CronJob** to run automatically:

- **CronJob Name**: `std-etl-ishares-components`
- **Namespace**: `etl`
- **Schedule**: `0 11 * * 0` (11:00 AM every Sunday)
- **TimeZone**: CET
- **History Limits**:
  - `successfulJobsHistoryLimit: 5`
  - `failedJobsHistoryLimit: 1`
- **Security & Resources**:
  - Runs as non-root user (UID/GID 1000)
  - Read-only root filesystem
  - Privilege escalation disabled
  - Resource requests: 500m CPU, 256Mi RAM
  - Resource limits: 4000m CPU, 2048Mi RAM

## Azure Resources

- **AKS Cluster**: Hosts the Kubernetes deployment.
- **Azure SQL DB**: Stores normalized ETF data.
- **ACR**: Stores Docker images.

## CI/CD with Azure Pipelines

The `azure-pipelines.yaml` defines a pipeline that:

1. Builds a Docker image.
2. Pushes the image to ACR with tags `latest` and timestamped builds.

Key variables in `azure-pipelines.yaml`:

```yaml
variables:
  dockerRegistryServiceConnection: 'pa-azure-container-registry'
  imageRepository: 'shares-components'
  dockerfilePath: '$(Build.SourcesDirectory)/Dockerfile'
  tag: $[format('{0:yyyy}.{0:MM}{0:dd}', pipeline.startTime)]
  buildId: $(Build.BuildId)
steps:
  - task: Docker@2
    displayName: Build and Push Docker Image
    inputs:
      containerRegistry: $(dockerRegistryServiceConnection)
      repository: $(imageRepository)
      command: buildAndPush
      dockerfile: $(dockerfilePath)
      tags:
        - latest
        - $(tag).$(buildId)
```

## Usage

**Local Run** (development/debugging):

```bash
export AZURE_SQL_...  # set necessary env vars
python main.py --workload-id YOUR_ID
```

**AKS Deployment**: Update your Kubernetes manifest or Helm chart to reference the ACR image `shares-components:latest`.

## Project Structure

```
├── azure-pipelines.yaml      # CI/CD definitions
├── Dockerfile                # Container image: Python 3.13.2, ODBC drivers, requirements
├── main.py                   # Entry point, parses args, starts ETL
├── core.py                   # Core orchestration logic
├── ishare.py                 # Scraping module via Bright Data proxy
├── transformer.py            # Data normalization functions
├── utils.py                  # Helper utilities
├── mssql.py                  # Azure SQL DB connector & queries
├── helper.py                 # Shared helper functions
├── settings.py               # Configuration loader
├── logger.py                 # Logging setup
└── README.md                 # Project documentation
```

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Create a Pull Request.

Please follow the project's code style and add tests where applicable.

## License

This project is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

## Contact

For questions or feedback, please open an issue or reach out to the maintainer at `clem@pvot.io`.

