"""
## Oracle ERP Data Pipeline Example

This DAG demonstrates how to connect to Oracle E-Business Suite (EBS) 
and extract data for analytics purposes.

Features:
- Secure connection using environment variables
- Error handling and logging
- Data validation
- Sample queries for common ERP tables

For production use, ensure proper security measures and access controls.
"""

from airflow.decorators import dag, task
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.models import Variable
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import logging
import os

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
    dag_id='oracle_erp_data_pipeline',
    default_args=default_args,
    description='Extract data from Oracle ERP system',
    schedule_interval='@daily',
    catchup=False,
    tags=['oracle', 'erp', 'data-pipeline'],
    doc_md=__doc__,
)
def oracle_erp_pipeline():
    
    @task
    def test_oracle_connection() -> Dict:
        """
        Test the Oracle ERP connection and return connection status
        """
        try:
            # Create Oracle connection using environment variables
            oracle_hook = OracleHook(
                oracle_conn_id='oracle_erp_dev',
                thick_mode=True  # Use thick mode for compatibility
            )
            
            # Test connection with a simple query
            connection = oracle_hook.get_conn()
            cursor = connection.cursor()
            
            # Simple test query
            cursor.execute("SELECT SYSDATE FROM DUAL")
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return {
                'status': 'success',
                'timestamp': str(result[0]),
                'message': 'Oracle ERP connection successful'
            }
            
        except Exception as e:
            logging.error(f"Oracle connection failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'message': 'Oracle ERP connection failed'
            }
    
    @task
    def extract_customer_data() -> List[Dict]:
        """
        Extract customer data from Oracle ERP
        Sample query for AR_CUSTOMERS table
        """
        try:
            oracle_hook = OracleHook(oracle_conn_id='oracle_erp_dev')
            
            # Sample query - adjust based on your ERP schema and requirements
            sql_query = """
            SELECT 
                CUSTOMER_ID,
                CUSTOMER_NAME,
                CUSTOMER_NUMBER,
                CREATION_DATE,
                LAST_UPDATE_DATE,
                STATUS
            FROM AR_CUSTOMERS 
            WHERE ROWNUM <= 100
            AND CREATION_DATE >= SYSDATE - 30
            ORDER BY CREATION_DATE DESC
            """
            
            # Execute query and fetch results
            df = oracle_hook.get_pandas_df(sql_query)
            
            # Convert to list of dictionaries for easier handling
            customer_data = df.to_dict('records')
            
            logging.info(f"Extracted {len(customer_data)} customer records")
            
            return customer_data
            
        except Exception as e:
            logging.error(f"Failed to extract customer data: {str(e)}")
            raise
    
    @task
    def extract_invoice_data() -> List[Dict]:
        """
        Extract invoice data from Oracle ERP
        Sample query for AR_INVOICES tables
        """
        try:
            oracle_hook = OracleHook(oracle_conn_id='oracle_erp_dev')
            
            # Sample query - adjust based on your ERP schema
            sql_query = """
            SELECT 
                INVOICE_ID,
                INVOICE_NUMBER,
                CUSTOMER_ID,
                INVOICE_DATE,
                TOTAL_AMOUNT,
                CURRENCY_CODE,
                STATUS
            FROM AR_INVOICES_ALL 
            WHERE ROWNUM <= 100
            AND INVOICE_DATE >= SYSDATE - 7
            ORDER BY INVOICE_DATE DESC
            """
            
            df = oracle_hook.get_pandas_df(sql_query)
            invoice_data = df.to_dict('records')
            
            logging.info(f"Extracted {len(invoice_data)} invoice records")
            
            return invoice_data
            
        except Exception as e:
            logging.error(f"Failed to extract invoice data: {str(e)}")
            raise
    
    @task
    def validate_and_process_data(customer_data: List[Dict], invoice_data: List[Dict]) -> Dict:
        """
        Validate and process the extracted data
        """
        try:
            # Basic validation
            customer_count = len(customer_data)
            invoice_count = len(invoice_data)
            
            # Data quality checks
            validation_results = {
                'customer_records': customer_count,
                'invoice_records': invoice_count,
                'validation_passed': True,
                'issues': []
            }
            
            # Check for minimum data requirements
            if customer_count == 0:
                validation_results['issues'].append('No customer data found')
                validation_results['validation_passed'] = False
            
            if invoice_count == 0:
                validation_results['issues'].append('No invoice data found')
                validation_results['validation_passed'] = False
            
            # Additional data quality checks can be added here
            
            logging.info(f"Data validation completed: {validation_results}")
            
            return validation_results
            
        except Exception as e:
            logging.error(f"Data validation failed: {str(e)}")
            raise
    
    @task
    def generate_summary_report(validation_results: Dict) -> Dict:
        """
        Generate a summary report of the data pipeline execution
        """
        try:
            report = {
                'pipeline_execution_time': datetime.now().isoformat(),
                'data_extraction_summary': validation_results,
                'status': 'completed' if validation_results['validation_passed'] else 'completed_with_issues',
                'next_steps': []
            }
            
            if not validation_results['validation_passed']:
                report['next_steps'].append('Review data quality issues')
                report['next_steps'].append('Check Oracle ERP system status')
            
            logging.info(f"Pipeline summary: {report}")
            
            return report
            
        except Exception as e:
            logging.error(f"Failed to generate summary report: {str(e)}")
            raise
    
    # Define task dependencies
    connection_test = test_oracle_connection()
    customer_data = extract_customer_data()
    invoice_data = extract_invoice_data()
    
    validation_results = validate_and_process_data(customer_data, invoice_data)
    summary_report = generate_summary_report(validation_results)
    
    # Set dependencies
    connection_test >> [customer_data, invoice_data]
    [customer_data, invoice_data] >> validation_results >> summary_report

# Instantiate the DAG
oracle_erp_pipeline()
