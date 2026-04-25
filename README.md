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
✅ **Mock Data Mode** - Demo without AWS credentials  

## Installation

```bash
# Clone the repository
cd /workspace

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### CLI Usage

```bash
# Run with mock data (no AWS credentials needed)
python main.py --mock

# Scan real AWS account
python main.py --region us-east-1 --days 7

# Save report to file
python main.py --mock --output report.txt

# Generate JSON report
python main.py --mock --format json --output report.json

# Show summary card only
python main.py --mock --format summary
```

### API Usage

```bash
# Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access interactive docs
http://localhost:8000/docs
```

#### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Welcome message |
| `GET /health` | Health check |
| `GET /scan` | Full scan with JSON response |
| `GET /scan/text` | Human-readable text report |
| `GET /scan/summary` | Quick summary card |
| `GET /scan/json` | Complete JSON analysis |

Example API call:
```bash
curl "http://localhost:8000/scan/text?use_mock_data=true"
```

## Project Structure

```
/workspace
├── main.py              # CLI entry point
├── ec2_scanner.py       # EC2 & CloudWatch scanning
├── idle_detector.py     # Idle instance detection logic
├── cost_calculator.py   # Cost calculation in INR/USD
├── report_generator.py  # Report generation (txt/json/csv)
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
python main.py --profile myprofile --region us-east-1
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

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please read context.md for implementation details.

---

**Built with ❤️ for cost-conscious startups**
