"""
## Oracle ERP Mock DAG

This DAG simulates Oracle ERP data extraction without requiring an actual Oracle connection.
It demonstrates the data pipeline structure and saves mock data to localhost.

Use this DAG to:
- Test the data pipeline workflow
- Generate sample ERP data for development
- Validate data storage and processing logic
"""

from airflow.decorators import dag, task
from airflow.datasets import Dataset
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import json
import csv
import os
import random

# Define datasets
oracle_customer_dataset = Dataset("oracle_customer_data")
oracle_invoice_dataset = Dataset("oracle_invoice_data")
oracle_processed_dataset = Dataset("oracle_processed_data")

# Default arguments for the DAG
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='oracle_erp_mock_pipeline',
    default_args=default_args,
    description='Mock Oracle ERP data pipeline for testing and development',
    schedule_interval='@daily',
    catchup=False,
    tags=['oracle', 'erp', 'mock', 'development'],
    doc_md=__doc__,
)
def oracle_erp_mock_pipeline():
    
    @task(outlets=[oracle_customer_dataset])
    def extract_mock_customer_data() -> List[Dict]:
        """
        Extract mock customer data simulating Oracle EBS AR_CUSTOMERS table
        """
        # Generate mock customer data similar to Oracle EBS structure
        mock_customers = []
        customer_names = [
            "ABC Corporation", "XYZ Industries", "Global Tech Solutions",
            "Metro Manufacturing", "Pacific Enterprises", "Atlantic Holdings",
            "Northern Logistics", "Southern Retail", "Eastern Imports",
            "Western Exports", "Central Services", "Coastal Trading"
        ]
        
        for i in range(1, len(customer_names) + 1):
            customer = {
                'customer_id': 1000 + i,
                'customer_number': f"CUST-{1000 + i}",
                'customer_name': customer_names[i-1],
                'customer_type': random.choice(['ORGANIZATION', 'PERSON']),
                'status': random.choice(['ACTIVE', 'INACTIVE']),
                'creation_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                'last_update_date': datetime.now().isoformat(),
                'credit_limit': round(random.uniform(10000, 500000), 2),
                'payment_terms': random.choice(['NET30', 'NET60', 'COD', 'PREPAID']),
                'address_line1': f"{random.randint(100, 9999)} Business St",
                'city': random.choice(['Bangkok', 'Chiang Mai', 'Phuket', 'Pattaya']),
                'postal_code': f"{random.randint(10000, 99999)}",
                'country': 'Thailand',
                'phone_number': f"+66-{random.randint(10000000, 99999999)}",
                'email': f"contact@{customer_names[i-1].lower().replace(' ', '').replace('.', '')}.com",
                'extracted_at': datetime.now().isoformat()
            }
            mock_customers.append(customer)
        
        # Save data to local file
        output_dir = "/opt/airflow/data_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as JSON
        json_file = f"{output_dir}/oracle_mock_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(mock_customers, f, indent=2)
        
        # Save as CSV
        csv_file = f"{output_dir}/oracle_mock_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            if mock_customers:
                writer = csv.DictWriter(f, fieldnames=mock_customers[0].keys())
                writer.writeheader()
                writer.writerows(mock_customers)
        
        logging.info(f"✅ Extracted {len(mock_customers)} mock customer records")
        logging.info(f"💾 Mock customer data saved to: {json_file}")
        logging.info(f"💾 Mock customer data saved to: {csv_file}")
        
        return mock_customers
    
    @task(outlets=[oracle_invoice_dataset])
    def extract_mock_invoice_data() -> List[Dict]:
        """
        Extract mock invoice data simulating Oracle EBS AR_INVOICES_ALL table
        """
        # Generate mock invoice data
        mock_invoices = []
        invoice_types = ['INVOICE', 'CREDIT_MEMO', 'DEBIT_MEMO']
        
        for i in range(1, 21):  # Generate 20 invoices
            invoice = {
                'invoice_id': 2000 + i,
                'invoice_number': f"INV-{datetime.now().year}-{2000 + i:04d}",
                'customer_id': 1000 + random.randint(1, 12),  # Reference to customers
                'invoice_type': random.choice(invoice_types),
                'invoice_date': (datetime.now() - timedelta(days=random.randint(1, 90))).date().isoformat(),
                'due_date': (datetime.now() + timedelta(days=random.randint(15, 60))).date().isoformat(),
                'invoice_amount': round(random.uniform(1000, 50000), 2),
                'tax_amount': 0,  # Will be calculated
                'total_amount': 0,  # Will be calculated
                'currency_code': 'THB',
                'payment_status': random.choice(['PAID', 'UNPAID', 'PARTIAL', 'OVERDUE']),
                'description': f"Invoice for services rendered - Period {random.randint(1, 12)}/2024",
                'creation_date': datetime.now().isoformat(),
                'last_update_date': datetime.now().isoformat(),
                'extracted_at': datetime.now().isoformat()
            }
            
            # Calculate tax (7% VAT)
            invoice['tax_amount'] = round(invoice['invoice_amount'] * 0.07, 2)
            invoice['total_amount'] = invoice['invoice_amount'] + invoice['tax_amount']
            
            mock_invoices.append(invoice)
        
        # Save data to local file
        output_dir = "/opt/airflow/data_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as JSON
        json_file = f"{output_dir}/oracle_mock_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(mock_invoices, f, indent=2)
        
        # Save as CSV
        csv_file = f"{output_dir}/oracle_mock_invoices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            if mock_invoices:
                writer = csv.DictWriter(f, fieldnames=mock_invoices[0].keys())
                writer.writeheader()
                writer.writerows(mock_invoices)
        
        logging.info(f"✅ Extracted {len(mock_invoices)} mock invoice records")
        logging.info(f"💾 Mock invoice data saved to: {json_file}")
        logging.info(f"💾 Mock invoice data saved to: {csv_file}")
        
        return mock_invoices
    
    @task(outlets=[oracle_processed_dataset])
    def process_oracle_analytics(customer_data: List[Dict], invoice_data: List[Dict]) -> Dict:
        """
        Process Oracle ERP analytics from customer and invoice data
        """
        # Calculate analytics
        total_customers = len(customer_data)
        active_customers = len([c for c in customer_data if c['status'] == 'ACTIVE'])
        total_invoices = len(invoice_data)
        
        # Financial metrics
        total_invoice_amount = sum(inv['invoice_amount'] for inv in invoice_data)
        total_tax_amount = sum(inv['tax_amount'] for inv in invoice_data)
        total_revenue = sum(inv['total_amount'] for inv in invoice_data)
        
        # Payment status analysis
        paid_invoices = len([inv for inv in invoice_data if inv['payment_status'] == 'PAID'])
        unpaid_invoices = len([inv for inv in invoice_data if inv['payment_status'] == 'UNPAID'])
        overdue_invoices = len([inv for inv in invoice_data if inv['payment_status'] == 'OVERDUE'])
        
        # Customer analysis
        avg_credit_limit = sum(c['credit_limit'] for c in customer_data) / len(customer_data)
        
        analytics_result = {
            'processing_date': datetime.now().isoformat(),
            'customer_metrics': {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'inactive_customers': total_customers - active_customers,
                'average_credit_limit': round(avg_credit_limit, 2)
            },
            'invoice_metrics': {
                'total_invoices': total_invoices,
                'total_invoice_amount': round(total_invoice_amount, 2),
                'total_tax_amount': round(total_tax_amount, 2),
                'total_revenue': round(total_revenue, 2),
                'average_invoice_amount': round(total_invoice_amount / total_invoices, 2) if total_invoices > 0 else 0
            },
            'payment_metrics': {
                'paid_invoices': paid_invoices,
                'unpaid_invoices': unpaid_invoices,
                'overdue_invoices': overdue_invoices,
                'payment_rate': round((paid_invoices / total_invoices) * 100, 2) if total_invoices > 0 else 0
            },
            'data_sources': {
                'customer_count': len(customer_data),
                'invoice_count': len(invoice_data)
            }
        }
        
        # Save analytics result to local file
        output_dir = "/opt/airflow/data_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save as JSON
        json_file = f"{output_dir}/oracle_mock_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(analytics_result, f, indent=2)
        
        # Save summary as CSV
        summary_data = []
        for category, metrics in analytics_result.items():
            if isinstance(metrics, dict):
                for metric, value in metrics.items():
                    summary_data.append({
                        'category': category,
                        'metric': metric,
                        'value': value,
                        'processed_at': analytics_result['processing_date']
                    })
        
        csv_file = f"{output_dir}/oracle_mock_analytics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            if summary_data:
                writer = csv.DictWriter(f, fieldnames=['category', 'metric', 'value', 'processed_at'])
                writer.writeheader()
                writer.writerows(summary_data)
        
        logging.info("📊 Oracle ERP Analytics processed successfully!")
        logging.info(f"💾 Analytics data saved to: {json_file}")
        logging.info(f"💾 Analytics summary saved to: {csv_file}")
        logging.info(f"📈 Total Revenue: ฿{analytics_result['invoice_metrics']['total_revenue']:,.2f}")
        logging.info(f"👥 Active Customers: {analytics_result['customer_metrics']['active_customers']}")
        logging.info(f"📄 Total Invoices: {analytics_result['invoice_metrics']['total_invoices']}")
        
        return analytics_result
    
    @task
    def generate_oracle_report(analytics_data: Dict) -> Dict:
        """
        Generate Oracle ERP executive summary report
        """
        report = {
            'report_title': 'Oracle ERP Daily Summary Report',
            'generated_at': datetime.now().isoformat(),
            'report_period': datetime.now().strftime('%Y-%m-%d'),
            'executive_summary': {
                'total_revenue': f"฿{analytics_data['invoice_metrics']['total_revenue']:,.2f}",
                'active_customers': analytics_data['customer_metrics']['active_customers'],
                'payment_rate': f"{analytics_data['payment_metrics']['payment_rate']}%",
                'avg_invoice_value': f"฿{analytics_data['invoice_metrics']['average_invoice_amount']:,.2f}"
            },
            'key_metrics': analytics_data,
            'recommendations': [
                "Monitor overdue invoices for collection",
                "Review credit limits for high-value customers",
                "Analyze payment patterns for cash flow optimization",
                "Consider payment term adjustments for better collection"
            ],
            'status': 'completed'
        }
        
        logging.info("📋 Oracle ERP Executive Report generated successfully!")
        logging.info(f"💰 Revenue Summary: {report['executive_summary']['total_revenue']}")
        logging.info(f"📊 Payment Rate: {report['executive_summary']['payment_rate']}")
        
        return report
    
    # Define task dependencies
    customer_data = extract_mock_customer_data()
    invoice_data = extract_mock_invoice_data()
    
    analytics_result = process_oracle_analytics(customer_data, invoice_data)
    final_report = generate_oracle_report(analytics_result)
    
    # Set dependencies
    [customer_data, invoice_data] >> analytics_result >> final_report

# Instantiate the DAG
oracle_erp_mock_pipeline()
