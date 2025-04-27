markdown
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Docker-Ready-blue" alt="Docker Ready">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue" alt="PostgreSQL 15">
  <img src="https://img.shields.io/badge/SpaceX-API-blue" alt="SpaceX API">
  <img src="https://img.shields.io/badge/Report-PDF-green" alt="PDF Report">
</p>

# SpaceX Launch Data Ingestion and Analysis

This project fetches, processes, stores, and analyzes launch data from the SpaceX public API.  
It uses PostgreSQL for storage, Trino as a query engine, and Python for ingestion, aggregation, analysis, and reporting.

---

## 1. Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone <your_repo_url>
   cd <project_folder>
2. **Start Docker services**
This project uses docker-compose.yml to start:
    - PostgreSQL database
    - Trino server
    - Python environment (with all dependencies installed)

    ```bash
    docker-compose up -d
✅ Note: You do NOT need to manually install any Python packages — they are installed automatically inside the Docker container via the Dockerfile.

3. **Check Docker containers**
    ```bash
    docker ps

## 2. Design Choices and Assumptions

### Database Design

- **PostgreSQL** is used to store:
  - `launches` table: Basic launch metadata.
  - `payloads` table: Payload information.
  - `aggregate_data_table`: Aggregated launch metrics for efficient querying.
- **Trino** is configured for external, scalable querying on top of PostgreSQL.

### Data Ingestion and Aggregation

- The **SpaceX API** (`v5/launches` and `v4/payloads`) is used as the external data source.
- Python scripts:
  - Fetch all launches and payloads.
  - Insert raw data into PostgreSQL.
  - Perform real-time aggregation:
    - Total number of launches.
    - Number of successful launches.
    - Average payload mass.
    - Average and maximum launch delays (in minutes).
  - Aggregated results are inserted into `aggregate_data_table`.

### Design Assumptions

- **Polling Strategy**:  
  No real-time push notification exists in SpaceX API, so periodic polling is used to detect new launches.

- **Launch Delay Calculation**:  
  Delay is calculated as the difference between `date_utc` and `date_local`.

- **Launchpad Information**:  
  Launchpad is stored by its **ID** (not human-readable name yet).

- **Payload Mass Handling**:  
  Payload mass per launch is averaged if multiple payloads are attached.

### Error Handling

- **Network Errors**:  
  API errors (connection failures, timeouts) are captured with retries and failover mechanisms.

- **Database Reset**:  
  During development mode, database tables are dropped and recreated when needed to avoid duplicate ingestion.


## 3. How to Test and Run the Ingestion and Aggregation

### Ingest All Launches

Run the ingestion script to:

- Fetch all launches from the SpaceX API.
- Fetch associated payloads.
- Insert data into PostgreSQL.
- Calculate and insert aggregation metrics per launch.

```bash
    python src/update_local_db_with_all_history.py
```

### Routine script
Run the routine script to:

- Check in 1Hz if new launch was updated in space-x api.
- Fetch new launch if exist.
- Fetch associated payloads.
- Insert data into PostgreSQL.
- Calculate and insert aggregation metrics per launch.

```bash
python src/routine_pipeline.py
```
✅ The routine runs continuously and updates the database automatically if new launches appear.

## 4. Project Structure

```bash
.
├── docker-compose.yml            # Docker Compose file for services
├── Dockerfile                     # Dockerfile for building the Python environment
├── requirements.txt               # Python dependencies
├── src/
│   ├── update_local_db_with_all_history.py            # Script to ingest all historical launches and payloads
│   ├── routine_pipeline.py        # Routine script to periodically fetch new launches
│   ├── db_server.py               # Database handler for PostgreSQL
│   ├── dataHolder/
│   │   ├── models.py              # Launch and Payload Pydantic models
│   │   ├── aggregate_data.py      # Aggregation metrics and table definition
│   │   └── data_holder_interface.py # Common interface for data holder classes
│   ├── api_reader.py              # Class to read data from SpaceX API
├── sql/
│   ├── data_analyzer.py           # Analyze and plot data from database
│   ├── generate_report.py         # Generate full PDF report
├── trino/
│   ├── etc/                       # Trino configuration files
└── README.md                      # (this file)



