#!/usr/bin/env python3
"""
AWS Cost Optimizer - Main CLI Tool
Scans EC2 instances, identifies idle resources, and calculates potential savings.

Usage:
    python main.py --region us-east-1 --days 7 --output report.txt
    python main.py --mock  # Run with mock data for demo
"""

import argparse
import sys
from datetime import datetime

from ec2_scanner import EC2Scanner
from idle_detector import IdleDetector
from cost_calculator import CostCalculator
from report_generator import ReportGenerator


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='AWS EC2 Cost Optimizer - Find idle instances and calculate savings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --region us-east-1 --days 7
  python main.py --mock --output report.txt
  python main.py --region ap-south-1 --cpu-threshold 10 --format json
        """
    )
    
    parser.add_argument(
        '--region', '-r',
        default='us-east-1',
        help='AWS region to scan (default: us-east-1)'
    )
    
    parser.add_argument(
        '--profile',
        help='AWS credentials profile name'
    )
    
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=7,
        help='Number of days for metrics analysis (default: 7)'
    )
    
    parser.add_argument(
        '--cpu-threshold',
        type=float,
        default=5.0,
        help='CPU threshold for idle detection in %% (default: 5%%)'
    )
    
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock data for demonstration'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: print to console)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'csv', 'summary'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def get_mock_instances():
    """Return mock instance data for testing/demo."""
    from datetime import timedelta
    
    now = datetime.utcnow()
    
    return [
        {
            'InstanceId': 'i-mock001',
            'InstanceType': 't3.medium',
            'State': 'running',
            'LaunchTime': now - timedelta(days=30),
            'Tags': {'Name': 'Dev-Server-1'},
            'Metrics': {
                'CPU': {'average': 2.5, 'maximum': 5.0, 'minimum': 0.5, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 50000, 'avg_network_out_bytes': 30000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-mock002',
            'InstanceType': 'm5.large',
            'State': 'running',
            'LaunchTime': now - timedelta(days=60),
            'Tags': {'Name': 'Prod-Web-1'},
            'Metrics': {
                'CPU': {'average': 45.0, 'maximum': 80.0, 'minimum': 20.0, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 5000000, 'avg_network_out_bytes': 3000000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-mock003',
            'InstanceType': 't2.micro',
            'State': 'stopped',
            'LaunchTime': now - timedelta(days=90),
            'Tags': {'Name': 'Old-Test-Server'},
            'Metrics': {
                'CPU': {'average': 0, 'maximum': 0, 'minimum': 0, 'datapoint_count': 0},
                'Network': {'avg_network_in_bytes': 0, 'avg_network_out_bytes': 0, 'datapoint_count': 0}
            }
        },
        {
            'InstanceId': 'i-mock004',
            'InstanceType': 't3.large',
            'State': 'running',
            'LaunchTime': now - timedelta(days=45),
            'Tags': {'Name': 'Staging-App'},
            'Metrics': {
                'CPU': {'average': 8.0, 'maximum': 25.0, 'minimum': 2.0, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 200000, 'avg_network_out_bytes': 150000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-mock005',
            'InstanceType': 'c5.xlarge',
            'State': 'running',
            'LaunchTime': now - timedelta(days=20),
            'Tags': {'Name': 'Compute-Heavy'},
            'Metrics': {
                'CPU': {'average': 3.0, 'maximum': 15.0, 'minimum': 0.5, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 80000, 'avg_network_out_bytes': 60000, 'datapoint_count': 7}
            }
        }
    ]


def main():
    """Main entry point."""
    args = parse_args()
    
    print("=" * 60)
    print("🚀 AWS EC2 COST OPTIMIZER")
    print("=" * 60)
    print(f"Region: {args.region}")
    print(f"Analysis Period: {args.days} days")
    print(f"CPU Threshold: {args.cpu_threshold}%")
    print("-" * 60)
    
    try:
        # Initialize components
        if args.mock:
            print("⚠️  Running with MOCK data for demonstration\n")
            instances = get_mock_instances()
        else:
            print(f"🔍 Scanning AWS EC2 instances in {args.region}...")
            scanner = EC2Scanner(region=args.region, profile_name=args.profile)
            instances = scanner.scan_all_instances(days=args.days)
        
        if not instances:
            print("\n✅ No EC2 instances found in the specified region.")
            return 0
        
        print(f"\n📊 Found {len(instances)} instances")
        
        # Analyze for idle instances
        print("\n🔎 Analyzing instance utilization...")
        detector = IdleDetector(cpu_threshold=args.cpu_threshold)
        analysis_result = detector.analyze_instances(instances)
        
        # Print summary
        summary = analysis_result['summary']
        print(f"\n📈 Analysis Summary:")
        print(f"   Total Instances: {summary['total_instances']}")
        print(f"   Idle Instances: {summary['idle_instances']}")
        print(f"   Stopped Abandoned: {summary['stopped_abandoned']}")
        print(f"   Underutilized: {summary['underutilized']}")
        print(f"   Healthy: {summary['healthy_instances']}")
        
        # Calculate costs and savings
        print("\n💰 Calculating costs and potential savings...")
        calculator = CostCalculator()
        cost_analysis = calculator.analyze_costs(instances, analysis_result)
        
        # Generate report
        generator = ReportGenerator()
        
        if args.format == 'summary':
            report = generator.generate_summary_card(cost_analysis)
        elif args.format == 'json':
            report = generator.generate_json_report(cost_analysis)
        elif args.format == 'csv':
            report = generator.generate_csv_report(cost_analysis)
        else:
            report = generator.generate_text_report(cost_analysis)
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n✅ Report saved to: {args.output}")
        else:
            print("\n")
            print(report)
        
        # Print the money shot
        savings = cost_analysis['summary']['potential_monthly_savings_inr']
        annual = cost_analysis['summary']['potential_annual_savings_inr']
        print("\n" + "=" * 60)
        print(f"🎯 Saved ₹{savings:,.2f} per month")
        print(f"💵 Saved ₹{annual:,.2f} per year")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
