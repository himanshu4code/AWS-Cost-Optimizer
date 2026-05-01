# AWS Cost Optimizer Tool

🚀 **Scan EC2 usage, find idle instances, and calculate potential cost savings in INR (₹)**

## Overview

This tool helps startups and businesses optimize their AWS EC2 costs by:
- Scanning all EC2 instances in a region
- Identifying idle and underutilized instances
- Detecting stopped instances that can be terminated
- Suggesting right-sizing opportunities
- Calculating potential monthly/yearly savings

## Features

✅ **EC2 Scanner** - Fetches all instances with CloudWatch metrics  
✅ **Idle Detection** - Identifies instances with CPU < 5% and low network activity  
✅ **Cost Calculator** - Calculates costs in INR with USD conversion  
✅ **"Saved ₹X per month"** - Shows potential savings simulation  
✅ **Multiple Output Formats** - Text, JSON, CSV reports  
✅ **REST API** - FastAPI-based API for integration  
✅ **Frontend UI** - React UI for credentials and insights  
✅ **AWS Credential Entry** - Users can submit and save their own AWS keys per scan  
✅ **Mock Data Mode** - Demo without AWS credentials  
✅ **Frontend App** - React UI for credentials and insights  
✅ **Dashboard Operations** - Dashboard, text, summary, and JSON scan views  

## Installation

```bash
# Clone the repository
cd /workspace

# Install dependencies
pip install -r requirements.txt

# Install frontend tooling
npm install
npm install --prefix frontend
```

## Quick Start

### CLI Usage

```bash
# Run with mock data (no AWS credentials needed)
python scripts/cost_optimizer.py --mock

# Scan real AWS account
python scripts/cost_optimizer.py --region us-east-1 --days 7

# Save report to file
python scripts/cost_optimizer.py --mock --output report.txt

# Generate JSON report
python scripts/cost_optimizer.py --mock --format json --output report.json

# Scan a real AWS account with direct credentials
python scripts/cost_optimizer.py --region us-east-1 --aws-access-key-id AKIA... --aws-secret-access-key ...

# Show summary card only
python scripts/cost_optimizer.py --mock --format summary
```

### Backend API (FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access interactive docs at:
http://localhost:8000/docs
http://localhost:8000/redoc
```

### Frontend (React + Vite)

```bash
# Install frontend dependencies
npm install --prefix frontend

# Start the frontend development server
npm --prefix frontend run dev

# Frontend will be available at:
http://localhost:5173
```

### Running Both Together

**Option 1: Start separately in two terminals**

Terminal 1 (Backend):
```bash
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
npm --prefix frontend run dev
```

**Option 2: Using Docker Compose (see below)**

### Environment Configuration

The frontend expects this environment variable:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

The backend expects the frontend origin for CORS:

```bash
FRONTEND_ORIGINS=http://localhost:5173
```

## Docker Compose

Run the entire application stack (FastAPI backend + React frontend) with a single command:

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Services will be available at:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Prerequisites:**
- Docker
- Docker Compose

**Configuration:**
Create a `.env` file in the root directory with your API and AWS settings:

```bash
VITE_API_BASE_URL=http://localhost:8000

FRONTEND_ORIGINS=http://localhost:5173
```

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message |
| `GET /health` | Health check |
| `GET /scan` | Full scan with JSON response |
| `POST /scan` | Scan using supplied AWS credentials |
| `POST /scan/text` | Text report scan |
| `POST /scan/summary` | Summary card scan |
| `POST /scan/json` | JSON analysis scan |
| `GET /scan/text` | Human-readable text report |
| `GET /scan/summary` | Quick summary card |
| `GET /scan/json` | Complete JSON analysis |

Example API call:
```bash
curl -H "Authorization: Bearer <access_token>" "http://localhost:8000/scan/text?use_mock_data=true"
```

## Project Structure

```
/workspace
├── main.py              # Backward-compatible CLI wrapper
├── ec2_scanner.py       # EC2 & CloudWatch scanning
├── idle_detector.py     # Idle instance detection logic
├── cost_calculator.py   # Cost calculation in INR/USD
├── report_generator.py  # Report generation (txt/json/csv)
├── scripts/
│   └── cost_optimizer.py # CLI entry point
├── requirements.txt     # Python dependencies
├── context.md           # Implementation context log
├── README.md            # This file
└── api/
    ├── __init__.py
    └── main.py          # FastAPI application
```

## Configuration

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--region` | us-east-1 | AWS region to scan |
| `--days` | 7 | Metrics analysis period |
| `--cpu-threshold` | 5.0 | CPU % below which = idle |
| `--mock` | False | Use demo data |
| `--format` | text | Output format |
| `--output` | console | Output file path |

### Environment Variables

For AWS authentication (when not using `--mock`):

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

Or use `~/.aws/credentials` profile:
```bash
python scripts/cost_optimizer.py --profile myprofile --region us-east-1
```

For local frontend and API configuration:

```bash
export VITE_API_BASE_URL=http://localhost:8000
export FRONTEND_ORIGINS=http://localhost:5173
```

## Sample Output

```
╔════════════════════════════════════════╗
║   💰 AWS COST OPTIMIZATION SUMMARY    ║
╠════════════════════════════════════════╣
║  Instances: 5                          ║
║  Current Cost: ₹34,156.00              ║
║  ─────────────────────────────────    ║
║  🎯 Saved ₹12,450 per month            ║
║  💵 Annual: ₹1,49,400                  ║
║  📉 Reduction: 36.5%                   ║
╚════════════════════════════════════════╝

🎯 Saved ₹12,450.00 per month
💵 Saved ₹1,49,400.00 per year
```

## How It Works

1. **Scan**: Fetches all EC2 instances and 7-day CloudWatch metrics
2. **Analyze**: Identifies idle (CPU < 5%), stopped (>7 days), underutilized
3. **Calculate**: Computes current costs and potential savings
4. **Report**: Generates actionable recommendations

### Detection Criteria

| Category | Criteria | Recommendation |
|----------|----------|----------------|
| Idle | CPU avg < 5%, Network < 1MB | Terminate |
| Stopped Abandoned | Stopped > 7 days | Terminate/Snapshot |
| Underutilized | CPU avg < 10%, Max < 50% | Right-size |

## Cost Calculation

Prices are based on AWS On-Demand rates (USD) converted to INR:
- Exchange rate: ~₹83/USD
- Includes compute + EBS storage (~₹500/month)
- Right-sizing suggestions with 30-70% savings

## Use Cases

### For Startups
- Reduce monthly AWS burn rate
- Identify forgotten resources
- Present savings to investors

### For Consultants
- Quick AWS cost audit tool
- Generate client-ready reports
- Demonstrate expertise

### For DevOps Teams
- Regular cost optimization checks
- CI/CD integration via API
- Automated reporting

## IAM Permissions Required

For real AWS scanning, minimum permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

## Disclaimer

⚠️ **Always review recommendations before taking action!**
- Verify instance importance before termination
- Create snapshots of important data
- Test in non-production first

## Frontend Setup

1. Set `VITE_API_BASE_URL` in `frontend/.env` or the root `.env` file.
2. Set `FRONTEND_ORIGINS` to the allowed browser origin for the backend.
3. Start the backend and frontend as separate processes or through Docker Compose.

The frontend sends AWS credentials only when you submit a scan, and the backend uses them for that request only.
If you enable "Remember AWS credentials on this device", the keys are stored in browser localStorage on that device only.

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read context.md for implementation details.

---

**Built with ❤️ for cost-conscious startups**
