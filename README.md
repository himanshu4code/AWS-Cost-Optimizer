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
✅ **Auth0 Login** - Frontend login and API token validation  
✅ **AWS Credential Entry** - Users can submit and save their own AWS keys per scan  
✅ **Mock Data Mode** - Demo without AWS credentials  
✅ **Frontend App** - React UI for login, credentials, and insights  
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

### API Usage

```bash
# Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access interactive docs
http://localhost:8000/docs
```

### Frontend Usage

```bash
# Start both frontend and backend from one command
npm run dev

# Or run the frontend separately
npm --prefix frontend run dev
```

The frontend expects these environment variables:

```bash
VITE_AUTH0_DOMAIN=your-tenant.us.auth0.com
VITE_AUTH0_CLIENT_ID=your_client_id
VITE_AUTH0_AUDIENCE=https://aws-cost-optimizer-api
VITE_API_BASE_URL=http://localhost:8000
```

The backend expects matching Auth0 settings:

```bash
AUTH0_DOMAIN=your-tenant.us.auth0.com
AUTH0_AUDIENCE=https://aws-cost-optimizer-api
AUTH0_CLIENT_ID=your_client_id
FRONTEND_ORIGIN=http://localhost:5173
```

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message |
| `GET /health` | Health check |
| `GET /auth/config` | Auth0 configuration for the frontend |
| `GET /scan` | Full scan with JSON response |
| `POST /scan` | Authenticated scan using user AWS credentials |
| `POST /scan/text` | Authenticated text report scan |
| `POST /scan/summary` | Authenticated summary card scan |
| `POST /scan/json` | Authenticated JSON analysis scan |
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

For Auth0-backed frontend and API authentication:

```bash
export AUTH0_DOMAIN=your-tenant.us.auth0.com
export AUTH0_AUDIENCE=https://aws-cost-optimizer-api
export AUTH0_CLIENT_ID=your_client_id
export FRONTEND_ORIGIN=http://localhost:5173
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

## Auth0 Setup

1. Create an Auth0 Single Page Application for the frontend.
2. Create an Auth0 API and set the audience to the same value used in `AUTH0_AUDIENCE`.
3. Add `http://localhost:5173` to the allowed callback and logout URLs.
4. Set the frontend variables in `frontend/.env` using the values from Auth0.
5. Set the backend variables before starting the API server.

The frontend sends AWS credentials only when you submit a scan, and the backend uses them for that request only.
If you enable "Remember AWS credentials on this device", the keys are stored in browser localStorage for that Auth0 user only.

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read context.md for implementation details.

---

**Built with ❤️ for cost-conscious startups**
