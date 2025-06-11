"""
## Dataset Example DAG

This DAG demonstrates how to create and use datasets in Airflow.
It shows how datasets are created when tasks complete successfully.

This is a working example that doesn't require external connections.
"""

from airflow.decorators import dag, task
from airflow.datasets import Dataset
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import json
import csv
import os

# Define datasets
customer_dataset = Dataset("customer_data")
sales_dataset = Dataset("sales_data")
processed_dataset = Dataset("processed_analytics")

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
    dag_id='dataset_example_pipeline',
    default_args=default_args,
    description='Example DAG showing dataset creation and usage',
    schedule_interval='@daily',
    catchup=False,
    tags=['example', 'datasets', 'demo'],
    doc_md=__doc__,
)
def dataset_example_pipeline():
    
    @task(outlets=[customer_dataset])
    def extract_customer_data() -> List[Dict]:
        """
        Extract customer data and create customer dataset
        """
        # Simulate customer data extraction
        customer_data = [
            {'customer_id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'created_at': datetime.now().isoformat()},
            {'customer_id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'created_at': datetime.now().isoformat()},
            {'customer_id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com', 'created_at': datetime.now().isoformat()},
        ]

        # Save data to local file
        output_dir = "/opt/airflow/data_output"
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        json_file = f"{output_dir}/customer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(customer_data, f, indent=2)

        # Save as CSV
        csv_file = f"{output_dir}/customer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            if customer_data:
                writer = csv.DictWriter(f, fieldnames=customer_data[0].keys())
                writer.writeheader()
                writer.writerows(customer_data)

        logging.info(f"Extracted {len(customer_data)} customer records")
        logging.info(f"💾 Data saved to: {json_file}")
        logging.info(f"💾 Data saved to: {csv_file}")
        logging.info("✅ Customer dataset created successfully!")

        return customer_data
    
    @task(outlets=[sales_dataset])
    def extract_sales_data() -> List[Dict]:
        """
        Extract sales data and create sales dataset
        """
        # Simulate sales data extraction
        sales_data = [
            {'sale_id': 1, 'customer_id': 1, 'amount': 100.50, 'date': '2024-01-01', 'extracted_at': datetime.now().isoformat()},
            {'sale_id': 2, 'customer_id': 2, 'amount': 250.75, 'date': '2024-01-02', 'extracted_at': datetime.now().isoformat()},
            {'sale_id': 3, 'customer_id': 1, 'amount': 75.25, 'date': '2024-01-03', 'extracted_at': datetime.now().isoformat()},
        ]

        # Save data to local file
        output_dir = "/opt/airflow/data_output"
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        json_file = f"{output_dir}/sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(sales_data, f, indent=2)

        # Save as CSV
        csv_file = f"{output_dir}/sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            if sales_data:
                writer = csv.DictWriter(f, fieldnames=sales_data[0].keys())
                writer.writeheader()
                writer.writerows(sales_data)

        logging.info(f"Extracted {len(sales_data)} sales records")
        logging.info(f"💾 Data saved to: {json_file}")
        logging.info(f"💾 Data saved to: {csv_file}")
        logging.info("✅ Sales dataset created successfully!")

        return sales_data
    
    @task(outlets=[processed_dataset])
    def process_analytics_data(customer_data: List[Dict], sales_data: List[Dict]) -> Dict:
        """
        Process analytics data and create processed dataset
        """
        # Simulate data processing
        total_customers = len(customer_data)
        total_sales = len(sales_data)
        total_revenue = sum(sale['amount'] for sale in sales_data)

        analytics_result = {
            'total_customers': total_customers,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'average_sale': total_revenue / total_sales if total_sales > 0 else 0,
            'processed_at': datetime.now().isoformat(),
            'customer_details': customer_data,
            'sales_details': sales_data
        }

        # Save analytics result to local file
        output_dir = "/opt/airflow/data_output"
        os.makedirs(output_dir, exist_ok=True)

        # Save as JSON
        json_file = f"{output_dir}/analytics_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(analytics_result, f, indent=2)

        # Save summary as CSV
        summary_data = [{
            'metric': 'total_customers',
            'value': total_customers,
            'processed_at': analytics_result['processed_at']
        }, {
            'metric': 'total_sales',
            'value': total_sales,
            'processed_at': analytics_result['processed_at']
        }, {
            'metric': 'total_revenue',
            'value': total_revenue,
            'processed_at': analytics_result['processed_at']
        }, {
            'metric': 'average_sale',
            'value': analytics_result['average_sale'],
            'processed_at': analytics_result['processed_at']
        }]

        csv_file = f"{output_dir}/analytics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['metric', 'value', 'processed_at'])
            writer.writeheader()
            writer.writerows(summary_data)

        logging.info(f"Analytics processed: {analytics_result}")
        logging.info(f"💾 Analytics data saved to: {json_file}")
        logging.info(f"💾 Analytics summary saved to: {csv_file}")
        logging.info("✅ Processed analytics dataset created successfully!")

        return analytics_result
    
    @task
    def generate_report(analytics_data: Dict) -> Dict:
        """
        Generate final report
        """
        report = {
            'report_title': 'Daily Analytics Report',
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'customers': analytics_data['total_customers'],
                'sales_count': analytics_data['total_sales'],
                'revenue': f"${analytics_data['total_revenue']:.2f}",
                'avg_sale': f"${analytics_data['average_sale']:.2f}"
            },
            'status': 'completed'
        }
        
        logging.info("📊 Report generated successfully!")
        logging.info(f"Report: {report}")
        
        return report
    
    # Define task dependencies
    customer_data = extract_customer_data()
    sales_data = extract_sales_data()
    
    analytics_result = process_analytics_data(customer_data, sales_data)
    final_report = generate_report(analytics_result)
    
    # Set dependencies
    [customer_data, sales_data] >> analytics_result >> final_report

# Instantiate the DAG
dataset_example_pipeline()


# Consumer DAG that runs when datasets are updated
@dag(
    dag_id='dataset_consumer_pipeline',
    default_args=default_args,
    description='DAG that runs when datasets are updated',
    schedule=[customer_dataset, sales_dataset],  # Triggered when these datasets are updated
    catchup=False,
    tags=['example', 'datasets', 'consumer'],
)
def dataset_consumer_pipeline():
    
    @task
    def process_updated_data() -> Dict:
        """
        Process data when datasets are updated
        """
        result = {
            'message': 'Processing triggered by dataset updates',
            'triggered_at': datetime.now().isoformat(),
            'datasets_updated': ['customer_data', 'sales_data']
        }
        
        logging.info("🔄 Consumer DAG triggered by dataset updates!")
        logging.info(f"Processing result: {result}")
        
        return result
    
    @task
    def send_notification(process_result: Dict) -> None:
        """
        Send notification about data processing
        """
        logging.info("📧 Sending notification about data processing completion")
        logging.info(f"Notification details: {process_result}")
        logging.info("✅ Notification sent successfully!")
    
    # Define task flow
    result = process_updated_data()
    send_notification(result)

# Instantiate the consumer DAG
dataset_consumer_pipeline()
