# AWS Cost Optimizer Tool - Implementation Context

## Project Overview
A script/API that scans EC2 usage, finds idle instances, and suggests cost savings with "Saved ₹X per month" simulation.

---

## Step-by-Step Implementation Log

### Step 1: Project Setup
**Date**: Initial setup
**Files Created**: 
- `context.md` (this file)
- `requirements.txt`

**Dependencies Added**:
```
boto3==1.34.0       # AWS SDK for Python
fastapi==0.109.0    # API framework
uvicorn==0.27.0     # ASGI server
pydantic==2.5.3     # Data validation
```

---

### Step 2: EC2 Scanner Module (`ec2_scanner.py`)
**Purpose**: Connect to AWS and fetch EC2 instances with CloudWatch metrics

**Key Classes/Functions**:
- `EC2Scanner` class
  - `__init__(region, profile_name)` - Initialize boto3 clients
  - `get_all_instances()` - Fetch all EC2 instances via pagination
  - `get_cpu_utilization(instance_id, days)` - Get CPU metrics from CloudWatch
  - `get_network_metrics(instance_id, days)` - Get NetworkIn/NetworkOut metrics
  - `scan_instance(instance, days)` - Scan single instance with all metrics
  - `scan_all_instances(days)` - Scan all instances in region

**Implementation Details**:
- Uses boto3 paginators for handling large instance counts
- Fetches 7-day metrics by default (configurable)
- Handles both running and stopped instances
- Returns structured dictionaries with instance info + metrics

**AWS APIs Used**:
- `ec2:DescribeInstances`
- `cloudwatch:GetMetricStatistics`

---

### Step 3: Idle Detector Module (`idle_detector.py`)
**Purpose**: Analyze instances and identify optimization opportunities

**Key Classes/Functions**:
- `IdleDetector` class
  - Configurable thresholds (CPU, network, stopped days)
  - `is_instance_idle(instance)` - Check if running instance is idle
  - `is_stopped_abandoned(instance)` - Check if stopped too long
  - `is_underutilized(instance)` - Check if can be rightsized
  - `analyze_instances(instances)` - Categorize all instances
  - `get_recommendations(analysis)` - Extract actionable recommendations

**Detection Criteria**:
| Category | Threshold | Action |
|----------|-----------|--------|
| Idle | CPU < 5%, Network < 1MB | Terminate |
| Stopped Abandoned | > 7 days stopped | Terminate/Snapshot |
| Underutilized | CPU avg < 10%, Max < 50% | Right-size |

**Output Categories**:
- `idle_instances` - Running but not used
- `stopped_abandoned` - Stopped for extended period
- `underutilized` - Could use smaller instance
- `healthy_instances` - Actively used, keep as-is

---

### Step 4: Cost Calculator Module (`cost_calculator.py`)
**Purpose**: Calculate costs and potential savings in INR (₹)

**Key Features**:
- Instance price lookup table (USD hourly rates)
- USD to INR conversion (₹83/USD)
- Right-sizing recommendation map
- Monthly cost calculation (730 hours/month)

**Key Classes/Functions**:
- `CostCalculator` class
  - `get_hourly_price_usd(instance_type)` - Lookup USD price
  - `get_hourly_price_inr(instance_type)` - Convert to INR
  - `get_monthly_cost_inr(instance_type)` - Monthly cost
  - `calculate_instance_cost(instance)` - Full cost breakdown
  - `calculate_savings_terminate(instance)` - Savings if terminated
  - `calculate_savings_rightsize(instance)` - Savings from right-sizing
  - `analyze_costs(instances, analysis)` - Complete cost analysis
  - `format_savings_display(savings_inr)` - Indian number format (L/Cr)

**Price Data Included**:
- t2, t3, t3a families
- m5, m5a families
- c5 family
- r5 family

**Right-size Mappings**:
- t3.2xlarge → t3.xlarge → t3.large → t3.medium → t3.small → t3.micro
- m5.4xlarge → m5.2xlarge → m5.xlarge → m5.large → t3.large
- Similar for c5, r5 families

---

### Step 5: Report Generator Module (`report_generator.py`)
**Purpose**: Generate human-readable reports with savings simulation

**Key Features**:
- Multiple output formats (text, JSON, CSV)
- "Saved ₹X per month" highlight
- Summary card for quick viewing
- Indian numbering system (Lakhs, Crores)

**Key Classes/Functions**:
- `ReportGenerator` class
  - `generate_text_report(cost_analysis)` - Full text report
  - `generate_json_report(cost_analysis)` - JSON format
  - `generate_csv_report(cost_analysis)` - CSV for spreadsheets
  - `generate_summary_card(cost_analysis)` - Compact summary box
  - `save_report(cost_analysis, path, format)` - Save to file

**Text Report Sections**:
1. Executive Summary
2. 💰 POTENTIAL SAVINGS SIMULATION (the money shot!)
3. Savings Breakdown
4. Idle Instances Details
5. Stopped Abandoned Details
6. Right-size Recommendations
7. Recommended Actions
8. Disclaimer

---

### Step 6: FastAPI Application (`api/main.py`)
**Purpose**: REST API for integration and web access

**Endpoints**:
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| GET | `/scan` | Full scan (JSON response) |
| GET | `/scan/text` | Human-readable report |
| GET | `/scan/summary` | Quick summary card |
| GET | `/scan/json` | Complete JSON analysis |

**Query Parameters**:
- `region` - AWS region (default: us-east-1)
- `cpu_threshold` - Idle CPU threshold (default: 5.0)
- `days` - Metrics period (default: 7)
- `use_mock_data` - Demo mode (default: false)

**Pydantic Models**:
- `SavingsSummary` - Summary data
- `InstanceRecommendation` - Per-instance recommendation
- `CostOptimizationReport` - Full API response

**Mock Data Function**:
- `get_mock_instances()` - Returns 5 sample instances for testing

---

### Step 7: CLI Tool (`main.py`)
**Purpose**: Command-line interface for direct usage

**Usage Examples**:
```bash
python main.py --mock                          # Demo with mock data
python main.py --region us-east-1 --days 7    # Real AWS scan
python main.py --mock -o report.txt           # Save to file
python main.py --mock -f json                 # JSON output
python main.py --mock -f summary              # Summary only
```

**CLI Arguments**:
- `--region/-r` - AWS region
- `--profile` - AWS credentials profile
- `--days/-d` - Analysis period
- `--cpu-threshold` - Idle detection threshold
- `--mock` - Use demo data
- `--output/-o` - Output file
- `--format/-f` - Output format (text/json/csv/summary)
- `--verbose/-v` - Debug output

---

### Step 8: Documentation (`README.md`)
**Contents**:
- Project overview
- Installation instructions
- Quick start guide
- CLI and API usage examples
- Project structure
- Configuration options
- Sample output
- Detection criteria
- IAM permissions required
- Use cases for startups/consultants

---

## File Structure Summary

```
/workspace
├── context.md              # This implementation log
├── README.md               # User documentation
├── requirements.txt        # Python dependencies
├── main.py                 # CLI entry point
├── ec2_scanner.py          # EC2 scanning module
├── idle_detector.py        # Idle detection logic
├── cost_calculator.py      # Cost calculation in INR
├── report_generator.py     # Report generation
└── api/
    ├── __init__.py
    └── main.py             # FastAPI application
```

---

## Key Design Decisions

1. **INR First**: All costs displayed in ₹ for Indian market, with USD equivalent
2. **Mock Data Mode**: Can demo without AWS credentials
3. **Modular Design**: Each module is independent and testable
4. **Configurable Thresholds**: CPU, network, days all adjustable
5. **Multiple Outputs**: Text for humans, JSON for machines, CSV for Excel
6. **Safe Recommendations**: Always includes disclaimer to review before action

---

## Testing Without AWS

Run with mock data:
```bash
python main.py --mock
```

This uses 5 pre-defined instances:
- i-mock001: t3.medium, idle (CPU 2.5%)
- i-mock002: m5.large, healthy (CPU 45%)
- i-mock003: t2.micro, stopped 90 days
- i-mock004: t3.large, underutilized (CPU 8%)
- i-mock005: c5.xlarge, idle (CPU 3%)

Expected output shows ~₹12,000-15,000 monthly savings.

---

## Next Steps / Enhancements

Potential future improvements:
1. Add RDS instance scanning
2. Add EBS volume analysis
3. Integrate AWS Pricing API for real-time prices
4. Add Reserved Instance recommendations
5. Add Savings Plans analysis
6. Multi-region scanning
7. Historical cost tracking
8. Slack/Email alerts
9. Web dashboard
10. Auto-remediation (with approval workflow)

---

## For Other Coding Agents

This repository is self-contained. To extend:
1. Read `context.md` for implementation history
2. Each module is documented with docstrings
3. Mock data allows testing without AWS
4. API has interactive docs at `/docs` when running

Key integration points:
- `ec2_scanner.py` - Add more metric types
- `idle_detector.py` - Add new detection rules
- `cost_calculator.py` - Update pricing data
- `api/main.py` - Add new endpoints
