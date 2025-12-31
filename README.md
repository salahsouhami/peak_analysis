PeakCost Control – Peak Analysis & Demand Charge Optimisation
PeakCost Control is an open‑source platform that helps commercial and industrial facilities understand and reduce electricity demand charges. These charges are determined by the highest 15‑minute demand interval during a billing period. By identifying when peaks occur and providing data‑driven strategies to avoid them, PeakCost Control turns quarter‑hour load curves into actionable business intelligence.
The repository is organised for extensibility – it supports one‑off analyses as well as continuous monitoring subscriptions. The core ideas are relevant across industries with high power demand such as cold‑storage logistics, manufacturing, automotive dealerships with EV charging, and other facilities subject to registered load measurement (RLM) tariffs.
Why Peak Cost Matters
Electricity bills are usually split into two components:
•	Arbeitspreis (energy price) – charged per kWh consumed. This is often stable or subject to simple tariffs.
•	Leistungspreis (demand price) – charged on the basis of the single highest 15‑minute demand (kW) recorded during a billing period. A single, poorly timed spike can dramatically increase annual costs.
PeakCost Control focuses on the demand price. Many organisations lack visibility into their load profiles and end up overpaying 20–30 % of their power bill because they are unaware of their load peaks or because operational patterns are not coordinated. By analysing data and suggesting operational adjustments, our solution can help achieve significant cost reductions without compromising production or quality.
Repository Overview
peak_analysis/
│
├── data/
│   └── raw/
│       └── input.xlsx           # Example 15‑minute load profile
│
├── n8n/                         # n8n workflow environment
│   ├── docker-compose.yml       # Defines n8n and supporting services
│   ├── Dockerfile               # Custom n8n image (optional)
│   ├── n8n_data/                # Persistent SQLite DB & workflows
│   └── n8n_files/               # Files accessible to n8n workflows
│       └── input.xlsx           # Same as data/raw input file
│
├── python/                      # Analysis service (FastAPI / Uvicorn)
│   ├── analysis_api.py          # Core peak detection and simulation logic
│   └── Dockerfile               # Python API container definition
│
├── slides/                      # Presentation material (optional)
│
└── README.md                    # You are here
n8n
n8n is a workflow automation tool. In this project it is used to orchestrate file ingestion and trigger the analysis service. Workflows read data from input.xlsx, convert it into JSON and call the Python API. n8n persists workflows and credentials in a SQLite database inside n8n_data/.
Python API
The python/analysis_api.py file defines a FastAPI service exposed on port 8000. The service accepts a JSON payload containing a list of quarter‑hour load records. It detects the maximum demand, calculates demand charges and can run scenarios such as load shifting. The API returns structured results that can be used in n8n workflows, dashboards or reports.
System Architecture
PeakCost Control consists of two loosely coupled services running in Docker containers:
┌──────────────┐       File ingest & triggers        ┌──────────────┐
│     n8n      │  ───────────────────────────────▶   │   FastAPI    │
│  Workflow    │                                      │  Analysis   │
│ Orchestration│  ◀───────────────────────────────   │  Service    │
└──────────────┘         JSON results via HTTP       └──────────────┘
     │
     └─ persistent volumes for workflow data and files
1.	Data ingestion – An operator exports quarter‑hour load data from the local metering system and saves it as input.xlsx or .csv. The file is placed into the n8n/n8n_files/ folder (volume‑mapped into the container).
2.	n8n workflow – n8n reads the file using the Read/Write File node, converts it to JSON with Extract from File (xlsx → JSON) and sends the payload via HTTP POST to the Python API running at http://host.docker.internal:8000/analyze. The workflow then processes the API response and writes reports or triggers notifications.
3.	Python API – The FastAPI application parses the data, identifies the maximum 15‑minute demand, calculates demand charges and optional scenario simulations (e.g. shifting defrost cycles). The API returns peaks, statistics and recommendations in JSON.
4.	Results – n8n can store results in a database, send an email, generate a PDF report or feed them back into other systems. This separation of orchestration and logic makes it easy to extend the solution.
Data Model
The API expects a JSON array of load records with a timestamp and average power in kilowatts. Example:
[
  {"timestamp": "2025-01-01T00:00:00", "power_kw": 85.0},
  {"timestamp": "2025-01-01T00:15:00", "power_kw": 80.5},
  ...
]
Internally the service assumes uniform 15‑minute spacing. It computes rolling maxima and identifies the highest value. Scenario modules may use additional fields (e.g. equipment status or process stage) to model operational constraints.
Quick Start
The simplest way to get started is using Docker Compose. Make sure you have Docker installed and, on Windows, the Windows Subsystem for Linux (WSL 2).
# Clone the repository
$ git clone https://github.com/<your‑org>/peak_analysis.git
$ cd peak_analysis

# Build and start services (first run can take a few minutes)
$ cd n8n
$ docker compose up -d  # starts both n8n and the Python API via Compose

# Access n8n
Open your browser and navigate to http://localhost:5678.  You will see the n8n web UI where you can import or build workflows.

# Place data file
Copy your load profile (XLSX) into `n8n/n8n_files/input.xlsx`.

# Test the API directly (optional)
$ curl -X POST http://localhost:8000/analyze \
       -H "Content-Type: application/json" \
       -d @path/to/sample.json
When both containers are running, the n8n workflow will automatically read the file and call the API. Watch the n8n execution logs to ensure there are no errors in the data format.
Creating the n8n Workflow
An example workflow might consist of the following nodes:
1.	Read from Disk – Reads input.xlsx from the /files/ directory inside the n8n container.
2.	Extract from File – Converts the binary data into a JSON array. Choose output format JSON. The sheet name should match the one in your Excel file.
3.	HTTP Request – Sends the JSON body to http://host.docker.internal:8000/analyze using the POST method. Set the body type to JSON and map the data from the previous node.
4.	Set / Transform – Processes the API response to extract peak values, cost savings and recommendations.
5.	Write to Disk / Send – Saves the results to a report file, sends them via email or triggers further actions.
n8n allows you to version your workflows; they are saved in the SQLite database under n8n_data/. You can export and commit workflows into your Git repository if desired.
Extending the Analysis – Industry Modules
PeakCost Control is designed to support industry‑specific modules. Each module encapsulates typical operational patterns and rules of thumb to model realistic peak shifting strategies. Examples include:
Industry / Use Case	Key Features and Optimisation Levers
Cold storage & logistics	Detects defrost cycles, compressor start‑ups and night cuts.
	Recommends shifting defrosting to off‑peak intervals or staggering multiple evaporators.
Manufacturing	Analyses machine clusters, welding robots, ovens. Suggests rescheduling batch processes or staggering start‑ups to avoid simultaneous peaks.
Automotive dealerships	Tracks EV charger demand and workshop equipment. Suggests load management for vehicle charging (smart scheduling, paused charging).
Metal processing	Considers furnace heating and large motors. Suggests smoothing start sequences and using inertial energy storage where feasible.
Logistics centres	Considers conveyor belts, sorting equipment and refrigerated loading docks. Suggests staging operations and controlling dock heaters.
To implement a module, extend the Python API with additional endpoints or configuration parameters. Each module can read its own configuration file (e.g. maximum shift duration, allowed deferral, temperature constraints) and calculate recommendations accordingly.
Best Practices & Recommendations
•	Data quality – Ensure your load profile has consistent 15‑minute intervals with time stamps in ISO‑8601 format. Missing or duplicated intervals can lead to incorrect peak identification.
•	Version control – Commit your workflows and API code to Git. This repository already contains docker-compose.yml and Dockerfile definitions for reproducible deployments.
•	Security – Protect n8n and the API behind a reverse proxy and configure authentication. The current setup exposes ports 5678 (n8n) and 8000 (API) locally.
•	Scalability – For continuous monitoring, deploy the containers on a server (cloud or on‑premises) and mount data volumes. Use n8n’s credential management for secure API calls and schedule workflows to run automatically.
•	Continuous improvement – Use the API results to refine operational processes. For example, coordinate production lines or refrigeration systems based on actual peaks rather than assumptions. Over time, integrate real‑time signals (e.g. machine status via OPC‑UA) to trigger dynamic peak avoidance.
Contributing
Contributions are welcome! To contribute a new module, fix a bug or improve documentation:
1.	Fork this repository on GitHub and create a feature branch.
2.	Make your changes following PEP 8 and n8n coding conventions.
3.	Add or update tests if applicable.
4.	Submit a pull request with a clear description of your changes.
License
This project is licensed under the MIT License. Feel free to use it in commercial or private projects; attribution is appreciated but not required.
________________________________________
About This README
This document is intentionally comprehensive to provide GitHub Copilot with context about the project’s purpose, structure and usage. With clear sections, Copilot can assist you in extending the analysis API, writing n8n workflows or integrating new industry modules. If you have questions or improvements, please open an issue or pull request.
________________________________________
