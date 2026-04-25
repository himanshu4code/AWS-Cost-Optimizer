"""
Report Generator Module
Generates human-readable cost optimization reports with savings simulations.
"""

import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from io import StringIO


class ReportGenerator:
    """Generates cost optimization reports in various formats."""
    
    def __init__(self, include_currency: str = 'INR'):
        """
        Initialize Report Generator.
        
        Args:
            include_currency: Currency to display (INR or USD)
        """
        self.currency = include_currency
    
    def _format_currency(self, amount: float, currency: str = 'INR') -> str:
        """Format amount as currency string."""
        if currency == 'INR':
            if amount >= 10000000:
                return f"₹{amount/10000000:.2f} Cr"
            elif amount >= 100000:
                return f"₹{amount/100000:.2f} L"
            elif amount >= 1000:
                return f"₹{amount/1000:.2f} K"
            else:
                return f"₹{amount:.2f}"
        else:  # USD
            if amount >= 10000:
                return f"${amount/1000:.2f} K"
            else:
                return f"${amount:.2f}"
    
    def generate_text_report(self, cost_analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable text report.
        
        Args:
            cost_analysis: Result from CostCalculator.analyze_costs()
            
        Returns:
            Formatted text report string
        """
        lines = []
        summary = cost_analysis.get('summary', {})
        breakdown = cost_analysis.get('breakdown', {})
        details = cost_analysis.get('details', {})
        
        # Header
        lines.append("=" * 80)
        lines.append("🚀 AWS EC2 COST OPTIMIZATION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {cost_analysis.get('analysis_timestamp', 'N/A')}")
        lines.append("")
        
        # Executive Summary
        lines.append("📊 EXECUTIVE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Instances Analyzed:     {summary.get('total_instances', 0)}")
        lines.append(f"Current Monthly Cost:         {self._format_currency(summary.get('total_current_monthly_cost_inr', 0), 'INR')}")
        lines.append(f"                              ({self._format_currency(summary.get('total_current_monthly_cost_usd', 0), 'USD')})")
        lines.append("")
        
        # THE MONEY SHOT - Savings Simulation
        lines.append("💰 POTENTIAL SAVINGS SIMULATION")
        lines.append("-" * 40)
        monthly_savings = summary.get('potential_monthly_savings_inr', 0)
        annual_savings = summary.get('potential_annual_savings_inr', 0)
        
        lines.append(f"🎯 Saved ₹{monthly_savings:,.2f} per month")
        lines.append(f"   (Approx ${summary.get('potential_monthly_savings_usd', 0):,.2f} USD)")
        lines.append("")
        lines.append(f"🎯 Saved ₹{annual_savings:,.2f} per year")
        lines.append(f"   (Approx ₹{annual_savings/100000:.2f} Lakhs annually)")
        lines.append("")
        lines.append(f"💡 This represents {summary.get('savings_percentage', 0):.1f}% cost reduction!")
        lines.append("")
        
        # Savings Breakdown
        lines.append("📈 SAVINGS BREAKDOWN")
        lines.append("-" * 40)
        lines.append(f"Idle Instances (Terminate):      {self._format_currency(breakdown.get('idle_instances_savings_inr', 0), 'INR')}/month")
        lines.append(f"Stopped Abandoned (Terminate):   {self._format_currency(breakdown.get('stopped_abandoned_savings_inr', 0), 'INR')}/month")
        lines.append(f"Underutilized (Rightsize):       {self._format_currency(breakdown.get('rightsize_savings_inr', 0), 'INR')}/month")
        lines.append("")
        
        # Idle Instances Details
        idle_instances = details.get('idle_instances', [])
        if idle_instances:
            lines.append("⚠️  IDLE INSTANCES (Recommended: TERMINATE)")
            lines.append("-" * 40)
            for inst in idle_instances:
                lines.append(f"  • {inst['InstanceId']} ({inst['InstanceType']})")
                lines.append(f"    Potential Savings: {self._format_currency(inst['monthly_savings_inr'], 'INR')}/month")
            lines.append("")
        
        # Stopped Abandoned Details
        stopped = details.get('stopped_abandoned', [])
        if stopped:
            lines.append("🛑 STOPPED ABANDONED INSTANCES (Recommended: TERMINATE OR SNAPSHOT)")
            lines.append("-" * 40)
            for inst in stopped:
                lines.append(f"  • {inst['InstanceId']} ({inst['InstanceType']})")
                lines.append(f"    Potential Savings: {self._format_currency(inst['monthly_savings_inr'], 'INR')}/month")
            lines.append("")
        
        # Right-size Recommendations
        rightsize = details.get('rightsize_recommendations', [])
        if rightsize:
            lines.append("📉 UNDERUTILIZED INSTANCES (Recommended: RIGHTSIZE)")
            lines.append("-" * 40)
            for rs in rightsize:
                lines.append(f"  • {rs['InstanceId']}: {rs['current_type']} → {rs['recommended_type']}")
                lines.append(f"    Current Cost: {self._format_currency(rs['current_monthly_cost_inr'], 'INR')}/month")
                lines.append(f"    New Cost: {self._format_currency(rs['new_monthly_cost_inr'], 'INR')}/month")
                lines.append(f"    Savings: {self._format_currency(rs['monthly_savings_inr'], 'INR')}/month ({rs['savings_percentage']}%)")
            lines.append("")
        
        # Action Items
        lines.append("✅ RECOMMENDED ACTIONS")
        lines.append("-" * 40)
        action_count = len(idle_instances) + len(stopped) + len(rightsize)
        if action_count > 0:
            lines.append(f"1. Review {len(idle_instances)} idle instances for termination")
            lines.append(f"2. Review {len(stopped)} stopped instances for cleanup")
            lines.append(f"3. Consider right-sizing {len(rightsize)} underutilized instances")
            lines.append("")
            lines.append(f"🎯 Total Actions: {action_count}")
            lines.append(f"💵 Total Monthly Savings: {self._format_currency(monthly_savings, 'INR')}")
        else:
            lines.append("✅ No immediate actions required. All instances appear to be optimally utilized.")
        lines.append("")
        
        # Footer
        lines.append("=" * 80)
        lines.append("⚠️  DISCLAIMER: These are recommendations only. Review before taking action.")
        lines.append("   Always verify instance importance before termination.")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_json_report(self, cost_analysis: Dict[str, Any], pretty: bool = True) -> str:
        """
        Generate a JSON report.
        
        Args:
            cost_analysis: Result from CostCalculator.analyze_costs()
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON string
        """
        if pretty:
            return json.dumps(cost_analysis, indent=2, default=str)
        else:
            return json.dumps(cost_analysis, default=str)
    
    def generate_csv_report(self, cost_analysis: Dict[str, Any]) -> str:
        """
        Generate a CSV report of all instances and recommendations.
        
        Args:
            cost_analysis: Result from CostCalculator.analyze_costs()
            
        Returns:
            CSV string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'InstanceId',
            'InstanceType',
            'State',
            'Recommendation',
            'Action',
            'Current_Monthly_Cost_INR',
            'Potential_Savings_INR',
            'Notes'
        ])
        
        # Process all instance costs
        all_costs = cost_analysis.get('all_instance_costs', [])
        details = cost_analysis.get('details', {})
        
        # Create lookup for recommendations
        recommendations = {}
        for inst in details.get('idle_instances', []):
            recommendations[inst['InstanceId']] = ('TERMINATE', inst['monthly_savings_inr'], 'Idle instance')
        for inst in details.get('stopped_abandoned', []):
            recommendations[inst['InstanceId']] = ('TERMINATE', inst['monthly_savings_inr'], 'Stopped > 7 days')
        for rs in details.get('rightsize_recommendations', []):
            recommendations[rs['InstanceId']] = ('RIGHTSIZE', rs['monthly_savings_inr'], f"Downsize to {rs['recommended_type']}")
        
        # Write rows
        for cost in all_costs:
            instance_id = cost.get('InstanceId', '')
            rec_info = recommendations.get(instance_id, ('KEEP', 0, 'Actively used'))
            
            writer.writerow([
                instance_id,
                cost.get('InstanceType', ''),
                cost.get('State', ''),
                rec_info[0],
                'Terminate' if rec_info[0] == 'TERMINATE' else ('Rightsize' if rec_info[0] == 'RIGHTSIZE' else 'None'),
                cost.get('total_monthly_cost_inr', 0),
                rec_info[1],
                rec_info[2]
            ])
        
        return output.getvalue()
    
    def generate_summary_card(self, cost_analysis: Dict[str, Any]) -> str:
        """
        Generate a compact summary card for quick viewing.
        
        Args:
            cost_analysis: Result from CostCalculator.analyze_costs()
            
        Returns:
            Compact summary string
        """
        summary = cost_analysis.get('summary', {})
        
        monthly_savings = summary.get('potential_monthly_savings_inr', 0)
        
        card = []
        card.append("╔════════════════════════════════════════╗")
        card.append("║   💰 AWS COST OPTIMIZATION SUMMARY    ║")
        card.append("╠════════════════════════════════════════╣")
        card.append(f"║  Instances: {summary.get('total_instances', 0):<28} ║")
        card.append(f"║  Current Cost: {self._format_currency(summary.get('total_current_monthly_cost_inr', 0)):<22} ║")
        card.append(f"║  ─────────────────────────────────    ║")
        card.append(f"║  🎯 Saved ₹{monthly_savings:,.0f} per month{' ' * 15} ║")
        card.append(f"║  💵 Annual: ₹{summary.get('potential_annual_savings_inr', 0):,.0f}{' ' * 16} ║")
        card.append(f"║  📉 Reduction: {summary.get('savings_percentage', 0):.1f}%{' ' * 22} ║")
        card.append("╚════════════════════════════════════════╝")
        
        return "\n".join(card)
    
    def save_report(self, cost_analysis: Dict[str, Any], output_path: str, format: str = 'txt') -> str:
        """
        Save report to a file.
        
        Args:
            cost_analysis: Result from CostCalculator.analyze_costs()
            output_path: Path to save the report
            format: Output format ('txt', 'json', 'csv')
            
        Returns:
            Path to saved file
        """
        if format == 'txt':
            content = self.generate_text_report(cost_analysis)
        elif format == 'json':
            content = self.generate_json_report(cost_analysis)
        elif format == 'csv':
            content = self.generate_csv_report(cost_analysis)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path


if __name__ == '__main__':
    # Example usage with mock data
    generator = ReportGenerator()
    
    mock_analysis = {
        'summary': {
            'total_instances': 10,
            'total_current_monthly_cost_inr': 50000,
            'total_current_monthly_cost_usd': 602.41,
            'potential_monthly_savings_inr': 15000,
            'potential_monthly_savings_usd': 180.72,
            'potential_annual_savings_inr': 180000,
            'savings_percentage': 30.0
        },
        'breakdown': {
            'idle_instances_savings_inr': 10000,
            'stopped_abandoned_savings_inr': 3000,
            'rightsize_savings_inr': 2000
        },
        'details': {
            'idle_instances': [
                {'InstanceId': 'i-123', 'InstanceType': 't3.medium', 'monthly_savings_inr': 5000},
                {'InstanceId': 'i-456', 'InstanceType': 't3.small', 'monthly_savings_inr': 5000}
            ],
            'stopped_abandoned': [
                {'InstanceId': 'i-789', 'InstanceType': 't2.micro', 'monthly_savings_inr': 3000}
            ],
            'rightsize_recommendations': [
                {
                    'InstanceId': 'i-abc',
                    'current_type': 'm5.large',
                    'recommended_type': 't3.large',
                    'current_monthly_cost_inr': 7000,
                    'new_monthly_cost_inr': 5000,
                    'monthly_savings_inr': 2000,
                    'savings_percentage': 28.57
                }
            ]
        },
        'all_instance_costs': [],
        'analysis_timestamp': datetime.utcnow().isoformat()
    }
    
    print(generator.generate_summary_card(mock_analysis))
    print("\n")
    print(generator.generate_text_report(mock_analysis))
