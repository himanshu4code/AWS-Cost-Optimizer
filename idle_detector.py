"""
Idle Instance Detector
Identifies idle and underutilized EC2 instances based on configurable thresholds.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class IdleDetector:
    """Detects idle and underutilized EC2 instances."""
    
    # Default thresholds
    DEFAULT_CPU_THRESHOLD = 5.0  # CPU < 5% considered idle
    DEFAULT_NETWORK_THRESHOLD = 1000000  # 1MB network traffic
    DEFAULT_STOPPED_DAYS_THRESHOLD = 7  # Stopped for > 7 days
    DEFAULT_MIN_DATAPPOINTS = 3  # Minimum datapoints for reliable analysis
    
    def __init__(
        self,
        cpu_threshold: float = DEFAULT_CPU_THRESHOLD,
        network_threshold: float = DEFAULT_NETWORK_THRESHOLD,
        stopped_days_threshold: int = DEFAULT_STOPPED_DAYS_THRESHOLD,
        min_datapoints: int = DEFAULT_MIN_DATAPPOINTS
    ):
        """
        Initialize Idle Detector.
        
        Args:
            cpu_threshold: CPU utilization threshold (percentage) below which instance is idle
            network_threshold: Network traffic threshold (bytes) below which instance is idle
            stopped_days_threshold: Days after which a stopped instance is considered abandoned
            min_datapoints: Minimum CloudWatch datapoints needed for reliable analysis
        """
        self.cpu_threshold = cpu_threshold
        self.network_threshold = network_threshold
        self.stopped_days_threshold = stopped_days_threshold
        self.min_datapoints = min_datapoints
    
    def is_instance_idle(self, instance: Dict[str, Any]) -> bool:
        """
        Check if an instance is idle based on CPU and network metrics.
        
        Args:
            instance: Scanned instance dictionary with metrics
            
        Returns:
            True if instance is idle, False otherwise
        """
        if instance['State'] != 'running':
            return False
        
        metrics = instance.get('Metrics', {})
        cpu_metrics = metrics.get('CPU', {})
        network_metrics = metrics.get('Network', {})
        
        # Check if we have enough datapoints
        if cpu_metrics.get('datapoint_count', 0) < self.min_datapoints:
            # Not enough data, check network instead
            if network_metrics.get('datapoint_count', 0) < self.min_datapoints:
                return False
        
        # Check CPU utilization
        avg_cpu = cpu_metrics.get('average', 100)
        if avg_cpu > self.cpu_threshold:
            return False
        
        # Check network activity
        avg_network_in = network_metrics.get('avg_network_in_bytes', float('inf'))
        avg_network_out = network_metrics.get('avg_network_out_bytes', float('inf'))
        
        if avg_network_in > self.network_threshold or avg_network_out > self.network_threshold:
            return False
        
        return True
    
    def is_stopped_abandoned(self, instance: Dict[str, Any]) -> bool:
        """
        Check if a stopped instance has been stopped for too long.
        
        Args:
            instance: Scanned instance dictionary
            
        Returns:
            True if stopped instance should be considered abandoned
        """
        if instance['State'] != 'stopped':
            return False
        
        launch_time = instance.get('LaunchTime')
        if not launch_time:
            return False
        
        # Note: For stopped instances, we'd ideally check StateTransitionReason
        # For simplicity, we'll flag all stopped instances older than threshold
        now = datetime.utcnow()
        
        # If launch time is old enough, consider it potentially abandoned
        if isinstance(launch_time, datetime):
            age_days = (now - launch_time).days
        else:
            # Parse ISO format string
            try:
                launch_dt = datetime.fromisoformat(launch_time.replace('Z', '+00:00'))
                age_days = (now - launch_dt).days
            except:
                return False
        
        return age_days >= self.stopped_days_threshold
    
    def is_underutilized(self, instance: Dict[str, Any], threshold_multiplier: float = 2.0) -> bool:
        """
        Check if an instance is significantly underutilized (could be rightsized).
        
        Args:
            instance: Scanned instance dictionary
            threshold_multiplier: Multiplier for CPU threshold to detect underutilization
            
        Returns:
            True if instance is underutilized and could be downsized
        """
        if instance['State'] != 'running':
            return False
        
        metrics = instance.get('Metrics', {})
        cpu_metrics = metrics.get('CPU', {})
        
        avg_cpu = cpu_metrics.get('average', 100)
        max_cpu = cpu_metrics.get('maximum', 100)
        
        # Underutilized: average CPU is very low AND max CPU never spikes high
        underutil_threshold = self.cpu_threshold * threshold_multiplier
        
        if avg_cpu < underutil_threshold and max_cpu < 50:  # Max never exceeds 50%
            return True
        
        return False
    
    def analyze_instances(self, instances: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all instances and categorize them.
        
        Args:
            instances: List of scanned instances
            
        Returns:
            Dictionary with categorized instances and summary
        """
        idle_instances = []
        stopped_abandoned = []
        underutilized = []
        healthy_instances = []
        
        for instance in instances:
            instance_id = instance['InstanceId']
            
            # Check for idle running instances
            if self.is_instance_idle(instance):
                idle_instances.append({
                    **instance,
                    'Recommendation': 'TERMINATE',
                    'Reason': f'CPU avg {instance["Metrics"]["CPU"]["average"]:.2f}% < {self.cpu_threshold}%'
                })
            # Check for abandoned stopped instances
            elif self.is_stopped_abandoned(instance):
                stopped_abandoned.append({
                    **instance,
                    'Recommendation': 'TERMINATE_OR_SNAPSHOT',
                    'Reason': f'Stopped for extended period'
                })
            # Check for underutilized instances
            elif self.is_underutilized(instance):
                underutilized.append({
                    **instance,
                    'Recommendation': 'RIGHTSIZE',
                    'Reason': f'Avg CPU {instance["Metrics"]["CPU"]["average"]:.2f}%, Max CPU {instance["Metrics"]["CPU"]["maximum"]:.2f}%'
                })
            else:
                healthy_instances.append({
                    **instance,
                    'Recommendation': 'KEEP',
                    'Reason': 'Instance is actively used'
                })
        
        return {
            'summary': {
                'total_instances': len(instances),
                'idle_instances': len(idle_instances),
                'stopped_abandoned': len(stopped_abandoned),
                'underutilized': len(underutilized),
                'healthy_instances': len(healthy_instances),
                'potential_savings_count': len(idle_instances) + len(stopped_abandoned) + len(underutilized)
            },
            'idle_instances': idle_instances,
            'stopped_abandoned': stopped_abandoned,
            'underutilized': underutilized,
            'healthy_instances': healthy_instances,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
    
    def get_recommendations(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract actionable recommendations from analysis.
        
        Args:
            analysis_result: Result from analyze_instances
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Add idle instances
        for inst in analysis_result.get('idle_instances', []):
            recommendations.append({
                'InstanceId': inst['InstanceId'],
                'InstanceType': inst['InstanceType'],
                'Action': 'TERMINATE',
                'Priority': 'HIGH',
                'Reason': inst['Reason'],
                'EstimatedSavings': '100% of instance cost'
            })
        
        # Add stopped abandoned
        for inst in analysis_result.get('stopped_abandoned', []):
            recommendations.append({
                'InstanceId': inst['InstanceId'],
                'InstanceType': inst['InstanceType'],
                'Action': 'TERMINATE_OR_SNAPSHOT',
                'Priority': 'MEDIUM',
                'Reason': inst['Reason'],
                'EstimatedSavings': '100% of instance cost'
            })
        
        # Add underutilized
        for inst in analysis_result.get('underutilized', []):
            recommendations.append({
                'InstanceId': inst['InstanceId'],
                'InstanceType': inst['InstanceType'],
                'Action': 'RIGHTSIZE',
                'Priority': 'MEDIUM',
                'Reason': inst['Reason'],
                'EstimatedSavings': '30-70% of instance cost'
            })
        
        return recommendations


if __name__ == '__main__':
    # Example usage with mock data
    detector = IdleDetector(cpu_threshold=5.0)
    
    mock_instances = [
        {
            'InstanceId': 'i-123456',
            'InstanceType': 't3.medium',
            'State': 'running',
            'Metrics': {
                'CPU': {'average': 2.5, 'maximum': 5.0, 'minimum': 0.5, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 50000, 'avg_network_out_bytes': 30000, 'datapoint_count': 7}
            }
        },
        {
            'InstanceId': 'i-789012',
            'InstanceType': 'm5.large',
            'State': 'running',
            'Metrics': {
                'CPU': {'average': 45.0, 'maximum': 80.0, 'minimum': 20.0, 'datapoint_count': 168},
                'Network': {'avg_network_in_bytes': 5000000, 'avg_network_out_bytes': 3000000, 'datapoint_count': 7}
            }
        }
    ]
    
    analysis = detector.analyze_instances(mock_instances)
    print(f"Analysis Summary: {analysis['summary']}")
    print(f"\nRecommendations:")
    for rec in detector.get_recommendations(analysis):
        print(f"  - {rec['InstanceId']}: {rec['Action']} ({rec['Priority']})")
