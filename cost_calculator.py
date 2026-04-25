"""
Cost Calculator Module
Calculates EC2 instance costs and potential savings in INR (₹).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class CostCalculator:
    """Calculates EC2 costs and potential savings."""
    
    # Approximate hourly prices for common instance types (USD)
    # In production, fetch from AWS Pricing API
    INSTANCE_PRICES_USD = {
        # t2 family
        't2.micro': 0.0116,
        't2.small': 0.023,
        't2.medium': 0.0464,
        't2.large': 0.0928,
        't2.xlarge': 0.1856,
        't2.2xlarge': 0.3712,
        
        # t3 family (cheaper, burstable)
        't3.micro': 0.0104,
        't3.small': 0.0208,
        't3.medium': 0.0416,
        't3.large': 0.0832,
        't3.xlarge': 0.1664,
        't3.2xlarge': 0.3328,
        
        # t3a family (AMD, even cheaper)
        't3a.micro': 0.0094,
        't3a.small': 0.0188,
        't3a.medium': 0.0376,
        't3a.large': 0.0752,
        
        # m5 family (general purpose)
        'm5.large': 0.096,
        'm5.xlarge': 0.192,
        'm5.2xlarge': 0.384,
        'm5.4xlarge': 0.768,
        
        # m5a family (AMD)
        'm5a.large': 0.086,
        'm5a.xlarge': 0.172,
        'm5a.2xlarge': 0.344,
        
        # c5 family (compute optimized)
        'c5.large': 0.085,
        'c5.xlarge': 0.17,
        'c5.2xlarge': 0.34,
        'c5.4xlarge': 0.68,
        
        # r5 family (memory optimized)
        'r5.large': 0.126,
        'r5.xlarge': 0.252,
        'r5.2xlarge': 0.504,
    }
    
    # Right-sizing recommendations (current -> smaller alternative)
    RIGHTSIZE_MAP = {
        't2.2xlarge': 't2.xlarge',
        't2.xlarge': 't2.large',
        't2.large': 't2.medium',
        't2.medium': 't2.small',
        't2.small': 't2.micro',
        
        't3.2xlarge': 't3.xlarge',
        't3.xlarge': 't3.large',
        't3.large': 't3.medium',
        't3.medium': 't3.small',
        't3.small': 't3.micro',
        
        'm5.4xlarge': 'm5.2xlarge',
        'm5.2xlarge': 'm5.xlarge',
        'm5.xlarge': 'm5.large',
        'm5.large': 't3.large',
        
        'c5.4xlarge': 'c5.2xlarge',
        'c5.2xlarge': 'c5.xlarge',
        'c5.xlarge': 'c5.large',
        
        'r5.2xlarge': 'r5.xlarge',
        'r5.xlarge': 'r5.large',
    }
    
    # USD to INR conversion rate (approximate)
    USD_TO_INR = 83.0
    
    # Hours in a month (average)
    HOURS_PER_MONTH = 730
    
    def __init__(self, usd_to_inr_rate: float = USD_TO_INR):
        """
        Initialize Cost Calculator.
        
        Args:
            usd_to_inr_rate: USD to INR conversion rate
        """
        self.usd_to_inr_rate = usd_to_inr_rate
    
    def get_hourly_price_usd(self, instance_type: str) -> float:
        """
        Get hourly price for an instance type in USD.
        
        Args:
            instance_type: EC2 instance type
            
        Returns:
            Hourly price in USD
        """
        return self.INSTANCE_PRICES_USD.get(instance_type, 0.0)
    
    def get_hourly_price_inr(self, instance_type: str) -> float:
        """
        Get hourly price for an instance type in INR.
        
        Args:
            instance_type: EC2 instance type
            
        Returns:
            Hourly price in INR
        """
        usd_price = self.get_hourly_price_usd(instance_type)
        return usd_price * self.usd_to_inr_rate
    
    def get_monthly_cost_inr(self, instance_type: str, hours: Optional[float] = None) -> float:
        """
        Calculate monthly cost for an instance type in INR.
        
        Args:
            instance_type: EC2 instance type
            hours: Hours per month (default: 730)
            
        Returns:
            Monthly cost in INR
        """
        if hours is None:
            hours = self.HOURS_PER_MONTH
        
        hourly_inr = self.get_hourly_price_inr(instance_type)
        return hourly_inr * hours
    
    def calculate_instance_cost(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate cost details for a single instance.
        
        Args:
            instance: Instance dictionary with InstanceType
            
        Returns:
            Dictionary with cost breakdown
        """
        instance_type = instance.get('InstanceType', 'unknown')
        state = instance.get('State', 'unknown')
        
        hourly_usd = self.get_hourly_price_usd(instance_type)
        hourly_inr = self.get_hourly_price_inr(instance_type)
        monthly_inr = self.get_monthly_cost_inr(instance_type)
        
        # If stopped, no compute charges (only storage)
        if state == 'stopped':
            # EBS storage cost approximation (~₹8/GB/month for gp3)
            storage_cost_inr = 500  # Assume ~60GB
            return {
                'InstanceId': instance.get('InstanceId'),
                'InstanceType': instance_type,
                'State': state,
                'hourly_cost_usd': 0,
                'hourly_cost_inr': 0,
                'monthly_compute_cost_inr': 0,
                'monthly_storage_cost_inr': storage_cost_inr,
                'total_monthly_cost_inr': storage_cost_inr,
                'currency': 'INR'
            }
        
        return {
            'InstanceId': instance.get('InstanceId'),
            'InstanceType': instance_type,
            'State': state,
            'hourly_cost_usd': round(hourly_usd, 4),
            'hourly_cost_inr': round(hourly_inr, 2),
            'monthly_compute_cost_inr': round(monthly_inr, 2),
            'monthly_storage_cost_inr': 500,  # EBS storage
            'total_monthly_cost_inr': round(monthly_inr + 500, 2),
            'currency': 'INR'
        }
    
    def calculate_savings_terminate(self, instance: Dict[str, Any]) -> float:
        """
        Calculate monthly savings if instance is terminated.
        
        Args:
            instance: Instance dictionary
            
        Returns:
            Monthly savings in INR
        """
        cost_info = self.calculate_instance_cost(instance)
        return cost_info['total_monthly_cost_inr']
    
    def calculate_savings_rightsize(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate savings from right-sizing an instance.
        
        Args:
            instance: Instance dictionary
            
        Returns:
            Dictionary with right-sizing details and savings
        """
        current_type = instance.get('InstanceType', '')
        
        if current_type not in self.RIGHTSIZE_MAP:
            return {
                'InstanceId': instance.get('InstanceId'),
                'current_type': current_type,
                'recommended_type': None,
                'current_monthly_cost_inr': 0,
                'new_monthly_cost_inr': 0,
                'monthly_savings_inr': 0,
                'savings_percentage': 0,
                'action': 'NO_RECOMMENDATION'
            }
        
        recommended_type = self.RIGHTSIZE_MAP[current_type]
        current_cost = self.get_monthly_cost_inr(current_type) + 500
        new_cost = self.get_monthly_cost_inr(recommended_type) + 500
        savings = current_cost - new_cost
        savings_pct = (savings / current_cost * 100) if current_cost > 0 else 0
        
        return {
            'InstanceId': instance.get('InstanceId'),
            'current_type': current_type,
            'recommended_type': recommended_type,
            'current_monthly_cost_inr': round(current_cost, 2),
            'new_monthly_cost_inr': round(new_cost, 2),
            'monthly_savings_inr': round(savings, 2),
            'savings_percentage': round(savings_pct, 2),
            'action': 'RIGHTSIZE'
        }
    
    def analyze_costs(self, instances: List[Dict[str, Any]], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze costs and calculate total potential savings.
        
        Args:
            instances: List of all scanned instances
            analysis_result: Result from IdleDetector.analyze_instances()
            
        Returns:
            Comprehensive cost analysis with savings projections
        """
        # Calculate costs for all instances
        instance_costs = []
        total_current_monthly_cost = 0
        
        for instance in instances:
            cost_info = self.calculate_instance_cost(instance)
            instance_costs.append(cost_info)
            total_current_monthly_cost += cost_info['total_monthly_cost_inr']
        
        # Calculate savings from idle instances (terminate)
        idle_savings = 0
        idle_details = []
        for inst in analysis_result.get('idle_instances', []):
            savings = self.calculate_savings_terminate(inst)
            idle_savings += savings
            idle_details.append({
                'InstanceId': inst['InstanceId'],
                'InstanceType': inst['InstanceType'],
                'monthly_savings_inr': round(savings, 2),
                'action': 'TERMINATE'
            })
        
        # Calculate savings from stopped abandoned (terminate)
        stopped_savings = 0
        stopped_details = []
        for inst in analysis_result.get('stopped_abandoned', []):
            savings = self.calculate_savings_terminate(inst)
            stopped_savings += savings
            stopped_details.append({
                'InstanceId': inst['InstanceId'],
                'InstanceType': inst['InstanceType'],
                'monthly_savings_inr': round(savings, 2),
                'action': 'TERMINATE'
            })
        
        # Calculate savings from underutilized (rightsize)
        rightsize_savings = 0
        rightsize_details = []
        for inst in analysis_result.get('underutilized', []):
            savings_info = self.calculate_savings_rightsize(inst)
            if savings_info['recommended_type']:
                rightsize_savings += savings_info['monthly_savings_inr']
                rightsize_details.append(savings_info)
        
        # Total potential savings
        total_potential_savings = idle_savings + stopped_savings + rightsize_savings
        
        return {
            'summary': {
                'total_instances': len(instances),
                'total_current_monthly_cost_inr': round(total_current_monthly_cost, 2),
                'total_current_monthly_cost_usd': round(total_current_monthly_cost / self.usd_to_inr_rate, 2),
                'potential_monthly_savings_inr': round(total_potential_savings, 2),
                'potential_monthly_savings_usd': round(total_potential_savings / self.usd_to_inr_rate, 2),
                'potential_annual_savings_inr': round(total_potential_savings * 12, 2),
                'savings_percentage': round((total_potential_savings / total_current_monthly_cost * 100) if total_current_monthly_cost > 0 else 0, 2)
            },
            'breakdown': {
                'idle_instances_savings_inr': round(idle_savings, 2),
                'stopped_abandoned_savings_inr': round(stopped_savings, 2),
                'rightsize_savings_inr': round(rightsize_savings, 2)
            },
            'details': {
                'idle_instances': idle_details,
                'stopped_abandoned': stopped_details,
                'rightsize_recommendations': rightsize_details
            },
            'all_instance_costs': instance_costs,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'currency': 'INR',
            'exchange_rate_used': self.usd_to_inr_rate
        }
    
    def format_savings_display(self, savings_inr: float) -> str:
        """
        Format savings amount for display with Indian numbering system.
        
        Args:
            savings_inr: Savings amount in INR
            
        Returns:
            Formatted string like "₹1,23,456"
        """
        # Convert to integer for formatting
        savings_int = int(savings_inr)
        
        # Indian numbering system
        if savings_int >= 10000000:  # Crores
            crores = savings_int / 10000000
            return f"₹{crores:.2f} Cr"
        elif savings_int >= 100000:  # Lakhs
            lakhs = savings_int / 100000
            return f"₹{lakhs:.2f} L"
        elif savings_int >= 1000:  # Thousands
            thousands = savings_int / 1000
            return f"₹{thousands:.2f} K"
        else:
            return f"₹{savings_int}"


if __name__ == '__main__':
    # Example usage
    calculator = CostCalculator()
    
    mock_instances = [
        {'InstanceId': 'i-123', 'InstanceType': 't3.medium', 'State': 'running'},
        {'InstanceId': 'i-456', 'InstanceType': 'm5.large', 'State': 'running'},
        {'InstanceId': 'i-789', 'InstanceType': 't2.micro', 'State': 'stopped'},
    ]
    
    print("Instance Costs:")
    for inst in mock_instances:
        cost = calculator.calculate_instance_cost(inst)
        print(f"  {inst['InstanceId']} ({inst['InstanceType']}): ₹{cost['total_monthly_cost_inr']}/month")
    
    print(f"\nRight-size example:")
    rs = calculator.calculate_savings_rightsize({'InstanceId': 'i-123', 'InstanceType': 't3.medium'})
    print(f"  Current: t3.medium (₹{rs['current_monthly_cost_inr']}/month)")
    print(f"  Recommended: {rs['recommended_type']} (₹{rs['new_monthly_cost_inr']}/month)")
    print(f"  Savings: ₹{rs['monthly_savings_inr']}/month ({rs['savings_percentage']}%)")
