# Incident Management System

A production-ready incident management system that automatically syncs Datadog alerts into a structured incident tracking system with lifecycle management, multiple storage backends, and cloud deployment capabilities.

## Overview

This system bridges the gap between Datadog monitoring and incident management by:

- Automatically converting Datadog alerts into trackable incidents
- Providing full lifecycle management (detected → acknowledged → resolved)
- Supporting multiple storage backends (JSON files for development, DynamoDB for production)
- Offering CLI tools and AWS Lambda deployment options

## Features

### Core Functionality

- **Automatic Alert Sync**: Fetches active alerts from Datadog and converts them to incidents
- **Duplicate Prevention**: Intelligently skips incidents that already exist based on Datadog alert IDs
- **Lifecycle Management**: Track incidents through detected → acknowledged → resolved states
- **Severity Mapping**: Automatically maps Datadog alert states to incident severity levels
- **Multiple Storage Backends**:
  - JSON file storage for local development
  - DynamoDB storage for production/cloud deployments

### Technical Features

- **Type-Safe Models**: Full type hints and validation
- **Comprehensive Testing**: 38+ unit tests with pytest
- **CI/CD Pipeline**: Automated testing and AWS Lambda deployment
- **CLI Interface**: Easy-to-use command-line tools
- **AWS Lambda Ready**: Serverless deployment support

## Architecture

```
src/
├── models/           # Data models (Incident, Metric)
├── storage/          # Storage abstractions (JSON, DynamoDB)
├── services/         # Business logic (IncidentService)
└── aws/              # AWS/Datadog integrations
```

The system follows a clean architecture pattern:

- **Models**: Domain entities (`Incident`, `Metric`)
- **Storage**: Abstraction layer allowing easy switching between backends
- **Services**: Business logic that orchestrates Datadog sync and incident management
- **AWS**: External API integrations (Datadog API client, DynamoDB)

## Setup

### Prerequisites

- Python 3.11+
- Datadog API credentials (API key and Application key)
- (Optional) AWS credentials for DynamoDB deployment

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd COX_Interview
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```bash
   DATADOG_API_KEY=your_api_key
   DATADOG_APP_KEY=your_app_key
   DATADOG_SITE=datadoghq.com  # Optional, defaults to US site
   ```

5. **Set up storage backend** (optional)

   For DynamoDB:

   ```bash
   export USE_DYNAMODB=true
   export DYNAMODB_TABLE_NAME=incidents  # Optional, defaults to 'incidents'
   ```

## Usage

### CLI Commands

**Sync Datadog alerts to incidents:**

```bash
python cli.py sync
```

**List all incidents:**

```bash
python cli.py list
```

### Using JSON Storage (Development)

```bash
python test_storage.py        # Test storage operations
python demo_service.py        # Demo service sync
```

### Using DynamoDB Storage (Production)

```bash
export USE_DYNAMODB=true
python cli.py sync
```

### Programmatic Usage

```python
from src.services.incident_service import IncidentService
from src.aws.datadog_client import DatadogClient
from src.storage.json_store import IncidentStore

# Initialize service
store = IncidentStore()
datadog_client = DatadogClient()
service = IncidentService(datadog_client=datadog_client, store=store)

# Sync alerts
new_incidents = service.sync_datadog_alerts()

# Get all incidents
all_incidents = service.get_all_incidents()

# Get active incidents (detected + acknowledged)
active = service.get_active_incidents()
```

## Incident Lifecycle

1. **Detected**: Incident created from Datadog alert
2. **Acknowledged**: Assigned to a team member
   ```python
   incident.acknowledge("John Doe")
   ```
3. **Resolved**: Marked as resolved with root cause
   ```python
   incident.resolve("Root cause here", ["Step 1", "Step 2"])
   ```

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Test coverage includes:

- Model validation and serialization
- Storage operations (save, load, query)
- Service layer business logic
- Datadog client integration
- Duplicate prevention logic

**Test Results**: 38 tests, all passing ✅

## Deployment

### AWS Lambda

The system includes a Lambda handler for serverless deployment:

```python
# lambda_function.py handles automatic deployment via CI/CD
```

**CI/CD Pipeline**:

- Automated testing on push to `main`
- Automatic Lambda deployment after successful tests
- DynamoDB table auto-creation if needed

**Required Lambda Environment Variables**:

- `DATADOG_API_KEY`
- `DATADOG_APP_KEY`
- `DYNAMODB_TABLE_NAME` (optional, defaults to 'incidents')

### Manual Lambda Deployment

1. Package the function:

   ```bash
   mkdir -p package
   cp -r src lambda_function.py package/
   pip install -r requirements.txt -t package/
   cd package && zip -r ../function.zip . && cd ..
   ```

2. Deploy to AWS:
   ```bash
   aws lambda update-function-code \
     --function-name incident-sync \
     --zip-file fileb://function.zip
   ```

## Project Structure

```
COX_Interview/
├── src/
│   ├── models/              # Domain models
│   │   ├── incident.py      # Incident model with lifecycle
│   │   └── metric.py        # Metric model
│   ├── storage/             # Storage implementations
│   │   ├── json_store.py    # JSON file storage
│   │   └── dynamodb_store.py # DynamoDB storage
│   ├── services/            # Business logic
│   │   └── incident_service.py
│   └── aws/                 # External integrations
│       ├── datadog_client.py
│       └── mock_datadog_client.py
├── tests/                   # Test suite
├── cli.py                   # CLI interface
├── lambda_function.py       # AWS Lambda handler
├── test_storage.py          # Storage demo script
├── demo_service.py          # Service demo script
├── requirements.txt         # Dependencies
└── .github/workflows/       # CI/CD pipeline
```

## Key Design Decisions

1. **Storage Abstraction**: Allows switching between JSON (dev) and DynamoDB (prod) without code changes
2. **Duplicate Prevention**: Uses Datadog alert ID to prevent duplicate incidents
3. **Severity Mapping**: Converts Datadog alert states (Alert, Warn, No Data) to standardized severity levels
4. **Type Safety**: Full type hints throughout for better IDE support and error prevention
5. **Clean Architecture**: Separation of concerns with models, storage, services, and integrations

## Environment Variables

| Variable              | Description             | Required | Default         |
| --------------------- | ----------------------- | -------- | --------------- |
| `DATADOG_API_KEY`     | Datadog API key         | Yes      | -               |
| `DATADOG_APP_KEY`     | Datadog Application key | Yes      | -               |
| `DATADOG_SITE`        | Datadog site            | No       | `datadoghq.com` |
| `USE_DYNAMODB`        | Use DynamoDB storage    | No       | `false`         |
| `DYNAMODB_TABLE_NAME` | DynamoDB table name     | No       | `incidents`     |
| `AWS_REGION`          | AWS region for DynamoDB | No       | `us-east-1`     |

## Contributing

1. Run tests before committing: `pytest tests/ -v`
2. Ensure all tests pass
3. Follow existing code style and type hints

## License

[Add your license here]
