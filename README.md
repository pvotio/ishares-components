# iShares Components
## Overview
iShares Components is a Python-based data pipeline that fetches, processes, and stores financial data related to iShares ETFs. It integrates with Microsoft SQL Server and utilizes proxy-based web scraping to collect and transform financial datasets.

## Features
- Fetches financial data from iShares ETF sources.
- Processes and cleans data using pandas and other utilities.
- Stores structured data into a Microsoft SQL database.
- Supports logging and configurable settings via environment variables.
- Dockerized deployment for easy scalability and portability.

## Installation
### Prerequisites
- Python 3.10+
- Microsoft SQL Server
- Docker (optional, for containerized execution)

### Setup
Clone the repository: 
```bash
git clone https://github.com/arqs-io/ishares-components.git 
cd ishares-components
```

Install dependencies: 
```bash
pip install -r requirements.txt
```

Set up environment variables:

- Copy .env.sample to .env
- Edit .env to include your database and proxy credentials.
- Run the application: `python main.py`

## Docker Usage
To run the application using Docker:

```bash
docker build -t ishares-components . 
docker run --env-file .env ishares-components
```

## Contributing
- Fork the repository.
- Create a feature branch: git checkout -b feature-branch
- Commit changes: git commit -m "Add new feature"
- Push to the branch: git push origin feature-branch
- Open a Pull Request.