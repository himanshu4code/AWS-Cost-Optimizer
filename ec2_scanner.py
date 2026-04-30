"""
EC2 Scanner Module
Scans AWS EC2 instances and collects metrics for cost optimization analysis.
"""

import boto3
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional


class EC2Scanner:
    """Scans EC2 instances and collects usage metrics."""
    
    def __init__(
        self,
        region: str = 'us-east-1',
        profile_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
    ):
        """
        Initialize EC2 Scanner.
        
        Args:
            region: AWS region to scan
            profile_name: AWS credentials profile name (optional)
        """
        session_kwargs = {'region_name': region}

        if profile_name:
            session_kwargs['profile_name'] = profile_name

        if aws_access_key_id and aws_secret_access_key:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key
            if aws_session_token:
                session_kwargs['aws_session_token'] = aws_session_token

        session = boto3.Session(**session_kwargs)
        self.ec2_client = session.client('ec2')
        self.cloudwatch_client = session.client('cloudwatch')
        
        self.region = region
    
    def get_all_instances(self) -> List[Dict[str, Any]]:
        """
        Fetch all EC2 instances in the region.
        
        Returns:
            List of instance dictionaries with basic info
        """
        instances = []
        paginator = self.ec2_client.get_paginator('describe_instances')
        
        for page in paginator.paginate():
            for reservation in page.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append({
                        'InstanceId': instance['InstanceId'],
                        'InstanceType': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'LaunchTime': instance['LaunchTime'],
                        'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                        'PrivateIpAddress': instance.get('PrivateIpAddress'),
                        'PublicIpAddress': instance.get('PublicIpAddress'),
                        'AvailabilityZone': instance['Placement']['AvailabilityZone'],
                    })
        
        return instances
    
    def get_cpu_utilization(self, instance_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get CPU utilization metrics for an instance.
        
        Args:
            instance_id: EC2 instance ID
            days: Number of days to look back
            
        Returns:
            Dictionary with average, maximum, minimum CPU utilization
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour periods
                Statistics=['Average', 'Maximum', 'Minimum']
            )
            
            datapoints = response.get('Datapoints', [])
            
            if not datapoints:
                return {
                    'average': 0,
                    'maximum': 0,
                    'minimum': 0,
                    'datapoint_count': 0
                }
            
            averages = [dp['Average'] for dp in datapoints]
            maximums = [dp['Maximum'] for dp in datapoints]
            minimums = [dp['Minimum'] for dp in datapoints]
            
            return {
                'average': sum(averages) / len(averages) if averages else 0,
                'maximum': max(maximums) if maximums else 0,
                'minimum': min(minimums) if minimums else 0,
                'datapoint_count': len(datapoints)
            }
        except Exception as e:
            print(f"Error fetching CPU metrics for {instance_id}: {e}")
            return {
                'average': 0,
                'maximum': 0,
                'minimum': 0,
                'datapoint_count': 0
            }
    
    def get_network_metrics(self, instance_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Get network I/O metrics for an instance.
        
        Args:
            instance_id: EC2 instance ID
            days: Number of days to look back
            
        Returns:
            Dictionary with network in/out metrics
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        try:
            # Network In
            response_in = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkIn',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day periods
                Statistics=['Average']
            )
            
            # Network Out
            response_out = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkOut',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=['Average']
            )
            
            datapoints_in = response_in.get('Datapoints', [])
            datapoints_out = response_out.get('Datapoints', [])
            
            avg_network_in = sum(dp['Average'] for dp in datapoints_in) / len(datapoints_in) if datapoints_in else 0
            avg_network_out = sum(dp['Average'] for dp in datapoints_out) / len(datapoints_out) if datapoints_out else 0
            
            return {
                'avg_network_in_bytes': avg_network_in,
                'avg_network_out_bytes': avg_network_out,
                'datapoint_count': len(datapoints_in)
            }
        except Exception as e:
            print(f"Error fetching network metrics for {instance_id}: {e}")
            return {
                'avg_network_in_bytes': 0,
                'avg_network_out_bytes': 0,
                'datapoint_count': 0
            }
    
    def scan_instance(self, instance: Dict[str, Any], days: int = 7) -> Dict[str, Any]:
        """
        Scan a single instance and collect all metrics.
        
        Args:
            instance: Instance dictionary from get_all_instances
            days: Number of days for metrics
            
        Returns:
            Complete instance data with metrics
        """
        instance_id = instance['InstanceId']
        
        # Only fetch CloudWatch metrics for running instances
        if instance['State'] == 'running':
            cpu_metrics = self.get_cpu_utilization(instance_id, days)
            network_metrics = self.get_network_metrics(instance_id, days)
        else:
            cpu_metrics = {'average': 0, 'maximum': 0, 'minimum': 0, 'datapoint_count': 0}
            network_metrics = {'avg_network_in_bytes': 0, 'avg_network_out_bytes': 0, 'datapoint_count': 0}
        
        return {
            **instance,
            'Metrics': {
                'CPU': cpu_metrics,
                'Network': network_metrics
            },
            'ScanTimestamp': datetime.now(timezone.utc).isoformat(),
        }
    
    def scan_all_instances(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Scan all instances and collect metrics.
        
        Args:
            days: Number of days for metrics
            
        Returns:
            List of all instances with their metrics
        """
        instances = self.get_all_instances()
        scanned_instances = []
        
        print(f"Scanning {len(instances)} instances...")
        
        for i, instance in enumerate(instances, 1):
            print(f"[{i}/{len(instances)}] Scanning {instance['InstanceId']}...")
            scanned_instance = self.scan_instance(instance, days)
            scanned_instances.append(scanned_instance)
        
        return scanned_instances


if __name__ == '__main__':
    # Example usage
    scanner = EC2Scanner(region='us-east-1')
    instances = scanner.scan_all_instances(days=7)
    print(f"\nScanned {len(instances)} instances")
    for inst in instances:
        print(f"  - {inst['InstanceId']}: {inst['State']} (Type: {inst['InstanceType']})")
